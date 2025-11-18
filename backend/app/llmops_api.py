"""
FastAPI Service for LLMOps Test Case Processing
Exposes LLMOps functionality as REST API endpoints
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from llmops import (
    TestCaseGenerator,
    ExcelReader,
    ExcelWriter,
    TestCase,
    TestCasePrompt,
    ExecutionResult,
    TestCaseStatus,
    get_config,
    PlaywrightAgent
)

# Initialize FastAPI app
app = FastAPI(
    title="LLMOps Test Case Processing API",
    description="API for processing test cases from Excel using LLM (Groq/OpenAI)",
    version="1.0.0"
)

# Initialize generator
generator = TestCaseGenerator()

# Pydantic models for API
class TestCaseRequest(BaseModel):
    test_id: str
    module: str
    functionality: str
    description: str
    steps: Optional[str] = None
    expected_result: Optional[str] = None
    priority: str = "Medium"

class TestCaseResponse(BaseModel):
    test_id: str
    module: str
    functionality: str
    description: str
    generated_prompt: str
    generated_at: str

class ConfigResponse(BaseModel):
    provider: str
    model: str
    temperature: float
    use_groq: bool

class PlaywrightExecutionRequest(BaseModel):
    """Request model for Playwright automation execution"""
    test_id: str = Field(..., description="Test case ID from generated prompt")
    generated_prompt: str = Field(..., description="Generated Playwright prompt from /generate-prompt endpoint")
    browser_type: str = Field(default="chromium", description="Browser type: chromium, firefox, or webkit")
    headless: bool = Field(default=False, description="Run browser in headless mode")
    max_iterations: int = Field(default=10, description="Maximum automation iterations")
    
class PlaywrightExecutionResponse(BaseModel):
    """Response model for Playwright automation execution"""
    test_id: str
    status: str  # "success", "failed", "error"
    execution_time: float
    steps_executed: int
    agent_output: str
    screenshots: List[str] = []
    error_message: Optional[str] = None
    executed_at: str

class BatchProcessRequest(BaseModel):
    test_cases: List[TestCaseRequest]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    provider: str
    model: str


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "message": "LLMOps Test Case Processing API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint with provider information"""
    config = get_config()
    provider_info = generator.get_provider_info()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        provider=provider_info["provider"],
        model=provider_info["model"]
    )


@app.get("/config", response_model=ConfigResponse, tags=["Configuration"])
async def get_configuration():
    """Get current LLM configuration"""
    config = get_config()
    provider_info = generator.get_provider_info()
    
    return ConfigResponse(
        provider=provider_info["provider"],
        model=provider_info["model"],
        temperature=provider_info["temperature"],
        use_groq=config.use_groq
    )


@app.post("/generate-prompt", response_model=TestCaseResponse, tags=["Test Case Processing"])
async def generate_single_prompt(request: TestCaseRequest):
    """
    Generate Playwright prompt for a single test case
    
    Args:
        request: Test case details
    
    Returns:
        Generated prompt with metadata
    """
    try:
        # Convert request to TestCase
        test_case = TestCase(
            test_id=request.test_id,
            module=request.module,
            functionality=request.functionality,
            description=request.description,
            steps=request.steps,
            expected_result=request.expected_result,
            priority=request.priority
        )
        
        # Generate prompt
        prompt = generator.generate_playwright_prompt(test_case)
        
        return TestCaseResponse(
            test_id=prompt.test_case.test_id,
            module=prompt.test_case.module,
            functionality=prompt.test_case.functionality,
            description=prompt.test_case.description,
            generated_prompt=prompt.generated_prompt or "",
            generated_at=prompt.generated_at.isoformat() if prompt.generated_at else datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating prompt: {str(e)}")


@app.post("/generate-prompts-batch", tags=["Test Case Processing"])
async def generate_batch_prompts(request: BatchProcessRequest):
    """
    Generate Playwright prompts for multiple test cases
    
    Args:
        request: List of test cases
    
    Returns:
        List of generated prompts
    """
    try:
        # Convert requests to TestCase objects
        test_cases = [
            TestCase(
                test_id=tc.test_id,
                module=tc.module,
                functionality=tc.functionality,
                description=tc.description,
                steps=tc.steps,
                expected_result=tc.expected_result,
                priority=tc.priority
            )
            for tc in request.test_cases
        ]
        
        # Generate prompts
        prompts = generator.generate_batch(test_cases)
        
        # Convert to response format
        responses = [
            {
                "test_id": p.test_case.test_id,
                "module": p.test_case.module,
                "functionality": p.test_case.functionality,
                "description": p.test_case.description,
                "generated_prompt": p.generated_prompt or "",
                "generated_at": p.generated_at.isoformat() if p.generated_at else datetime.now().isoformat()
            }
            for p in prompts
        ]
        
        return {
            "total": len(responses),
            "prompts": responses
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating batch prompts: {str(e)}")


@app.post("/upload-excel", tags=["Excel Processing"])
async def upload_excel_and_process(
    file: UploadFile = File(...),
    sheet_name: str = "Sheet1"
):
    """
    Upload Excel file and generate prompts for all test cases
    
    Args:
        file: Excel file with test cases
        sheet_name: Name of the sheet to process
    
    Returns:
        Generated prompts for all test cases
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be an Excel file (.xlsx or .xls)")
    
    try:
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            # Process Excel file
            prompts = generator.process_excel(tmp_path, sheet_name=sheet_name)
            
            # Convert to response format
            responses = [
                {
                    "test_id": p.test_case.test_id,
                    "module": p.test_case.module,
                    "functionality": p.test_case.functionality,
                    "description": p.test_case.description,
                    "generated_prompt": p.generated_prompt or "",
                    "generated_at": p.generated_at.isoformat() if p.generated_at else datetime.now().isoformat()
                }
                for p in prompts
            ]
            
            return {
                "filename": file.filename,
                "sheet_name": sheet_name,
                "total_test_cases": len(responses),
                "prompts": responses
            }
        
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Excel file: {str(e)}")


@app.post("/read-excel", tags=["Excel Processing"])
async def read_excel_test_cases(
    file: UploadFile = File(...),
    sheet_name: str = "Sheet1"
):
    """
    Read test cases from Excel file without generating prompts
    
    Args:
        file: Excel file with test cases
        sheet_name: Name of the sheet to read
    
    Returns:
        List of test cases from Excel
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be an Excel file (.xlsx or .xls)")
    
    try:
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            # Read test cases
            test_cases = generator.read_test_cases(tmp_path, sheet_name=sheet_name)
            
            # Convert to dict format
            responses = [tc.to_dict() for tc in test_cases]
            
            return {
                "filename": file.filename,
                "sheet_name": sheet_name,
                "total_test_cases": len(responses),
                "test_cases": responses
            }
        
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading Excel file: {str(e)}")


@app.get("/test-case/{test_id}", tags=["Test Case Management"])
async def get_test_case(test_id: str, file_path: str, sheet_name: str = "Sheet1"):
    """
    Get a specific test case by ID from Excel file
    
    Args:
        test_id: Test case ID to retrieve
        file_path: Path to Excel file
        sheet_name: Sheet name
    
    Returns:
        Test case details
    """
    try:
        reader = ExcelReader(file_path, sheet_name)
        test_case = reader.get_test_case_by_id(test_id)
        
        if test_case is None:
            raise HTTPException(status_code=404, detail=f"Test case {test_id} not found")
        
        return test_case.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving test case: {str(e)}")


@app.get("/providers", tags=["Configuration"])
async def list_providers():
    """List available LLM providers and their configurations"""
    config = get_config()
    
    providers = {
        "groq": {
            "available": bool(config.groq_api_key),
            "model": config.groq_model,
            "temperature": config.temperature
        },
        "openai": {
            "available": bool(config.openai_api_key or config.custom_openai_key),
            "model": "gpt-4o",
            "temperature": config.temperature,
            "custom_gateway": bool(getattr(config, 'custom_openai_base_url', None))
        }
    }
    
    return {
        "current_provider": "groq" if config.use_groq else "openai",
        "providers": providers
    }


@app.post("/change-provider", tags=["Configuration"])
async def change_provider(provider: str):
    """
    Change LLM provider (groq or openai)
    
    Note: This changes the environment variable for the current session
    """
    if provider.lower() not in ["groq", "openai"]:
        raise HTTPException(status_code=400, detail="Provider must be 'groq' or 'openai'")
    
    try:
        # Update environment variable
        os.environ["USE_GROQ"] = "true" if provider.lower() == "groq" else "false"
        
        # Reinitialize generator with new provider
        global generator
        generator = TestCaseGenerator()
        
        provider_info = generator.get_provider_info()
        
        return {
            "message": f"Provider changed to {provider}",
            "current_provider": provider_info["provider"],
            "model": provider_info["model"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error changing provider: {str(e)}")


@app.post("/execute-playwright", response_model=PlaywrightExecutionResponse, tags=["Playwright Automation"])
async def execute_playwright_automation(request: PlaywrightExecutionRequest):
    """
    Execute Playwright automation based on generated prompt
    
    This endpoint takes the output from /generate-prompt and executes
    the automated test using Playwright agent.
    
    Args:
        request: Contains test_id, generated_prompt, and browser settings
    
    Returns:
        Execution results with status, steps, and screenshots
    
    Example workflow:
        1. POST /generate-prompt -> Get generated_prompt
        2. POST /execute-playwright -> Execute automation with the prompt
    """
    import time
    
    try:
        start_time = time.time()
        
        # Initialize Playwright Agent
        # Get custom OpenAI config from environment
        api_key = os.getenv("CUSTOM_OPENAI_KEY")
        gateway_url = os.getenv("CUSTOM_OPENAI_GATEWAY_URL")
        model = os.getenv("CUSTOM_OPENAI_MODEL", "gpt-4o")
        
        if not api_key:
            raise HTTPException(
                status_code=400, 
                detail="CUSTOM_OPENAI_KEY environment variable not set. Required for Playwright agent."
            )
        
        agent = PlaywrightAgent(
            api_key=api_key,
            model=model,
            gateway_url=gateway_url
        )
        
        # Execute the automation with the generated prompt
        result = await agent.run(
            task=request.generated_prompt,
            max_iterations=request.max_iterations
        )
        
        execution_time = time.time() - start_time
        
        # Parse the result to extract useful information
        agent_output = str(result) if result else "No output"
        
        # Count steps executed (messages in the conversation)
        steps_executed = len(result.get("messages", [])) if isinstance(result, dict) else 0
        
        # Check if automation completed successfully
        # Consider it successful if browser navigation occurred and no errors
        is_success = "error" not in agent_output.lower() and "failed" not in agent_output.lower()
        status = "success" if is_success else "failed"
        
        # Look for screenshot mentions in output
        screenshots = []
        import re
        screenshot_matches = re.findall(r'screenshot.*?([a-zA-Z0-9_-]+\.png)', agent_output, re.IGNORECASE)
        screenshots.extend(screenshot_matches)
        
        return PlaywrightExecutionResponse(
            test_id=request.test_id,
            status=status,
            execution_time=round(execution_time, 2),
            steps_executed=steps_executed,
            agent_output=agent_output,
            screenshots=screenshots,
            error_message=None if is_success else "Automation encountered issues. Check agent_output for details.",
            executed_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return PlaywrightExecutionResponse(
            test_id=request.test_id,
            status="error",
            execution_time=round(execution_time, 2),
            steps_executed=0,
            agent_output="",
            screenshots=[],
            error_message=str(e),
            executed_at=datetime.now().isoformat()
        )


@app.post("/execute-playwright-from-testcase", response_model=PlaywrightExecutionResponse, tags=["Playwright Automation"])
async def execute_playwright_from_testcase(request: TestCaseRequest):
    """
    Combined endpoint: Generate prompt AND execute Playwright automation
    
    This is a convenience endpoint that combines /generate-prompt and /execute-playwright
    into a single call for end-to-end automation.
    
    Args:
        request: Test case details (same as /generate-prompt)
    
    Returns:
        Execution results with generated prompt and automation status
    """
    try:
        # Step 1: Generate prompt
        test_case = TestCase(
            test_id=request.test_id,
            module=request.module,
            functionality=request.functionality,
            description=request.description,
            steps=request.steps,
            expected_result=request.expected_result,
            priority=request.priority
        )
        
        prompt_result = generator.generate_playwright_prompt(test_case)
        generated_prompt = prompt_result.generated_prompt
        
        if not generated_prompt:
            raise HTTPException(status_code=500, detail="Failed to generate prompt")
        
        # Step 2: Execute automation with generated prompt
        exec_request = PlaywrightExecutionRequest(
            test_id=request.test_id,
            generated_prompt=generated_prompt,
            browser_type="chromium",
            headless=False,
            max_iterations=10
        )
        
        return await execute_playwright_automation(exec_request)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in combined execution: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("LLMOps Test Case Processing API")
    print("=" * 70)
    
    # Show current configuration
    config = get_config()
    provider_info = generator.get_provider_info()
    
    print(f"\n✓ Provider: {provider_info['provider']}")
    print(f"✓ Model: {provider_info['model']}")
    print(f"✓ Temperature: {provider_info['temperature']}")
    
    print("\n" + "=" * 70)
    print("Starting server on http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("=" * 70 + "\n")
    
    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000)
