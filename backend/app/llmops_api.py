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
from llmops.common.logger import (
    log_info,
    log_error,
    log_warning,
    log_llm,
    log_prompt,
    get_logger
)
from llmops.common.exceptions import (
    ValidationException,
    InvalidInputException,
    StateException,
    LLMException,
    PlaywrightException,
    ConfigurationException
)

config = get_config()
logger = get_logger(__name__)
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
    browser_type: str = Field(default="chromium", description="Browser type: chromium, firefox, webkit, or edge")

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
    browser_type: str = Field(default="chromium", description="Browser type: chromium, firefox, webkit, or edge")
    headless: bool = Field(default=False, description="Run browser in headless mode")
    max_iterations: int = Field(default=10, description="Maximum automation iterations")
    
class ElementMetadata(BaseModel):
    """Metadata for a single element"""
    id: str = Field(..., description="Element identifier")
    type: str = Field(..., description="Element type (link, button, input, etc.)")
    tag: str = Field(..., description="HTML tag name")
    text: Optional[str] = Field(None, description="Element text content")
    element_id: Optional[str] = Field(None, description="HTML id attribute", alias="id_attr")
    name: Optional[str] = Field(None, description="Element name attribute")
    class_name: Optional[str] = Field(None, description="Element class attribute", alias="class")
    href: Optional[str] = Field(None, description="Link href attribute")
    input_type: Optional[str] = Field(None, description="Input type attribute")
    depends_on: List[str] = Field(default_factory=list, description="Dependencies on other elements")
    
class PageMetadata(BaseModel):
    """Metadata for a page"""
    url: str = Field(..., description="Page URL")
    title: str = Field(..., description="Page title")
    key_elements: List[ElementMetadata] = Field(default_factory=list, description="Key elements on the page")

class PageNode(BaseModel):
    """Page node with metadata"""
    id: str = Field(..., description="Page node identifier")
    label: str = Field(..., description="Page label with title and domain")
    x: int = Field(default=200, description="X coordinate for visualization")
    y: int = Field(default=100, description="Y coordinate for visualization")
    metadata: PageMetadata = Field(..., description="Page metadata with elements")

class Edge(BaseModel):
    """Edge connecting two pages"""
    source: str = Field(..., description="Source page node ID")
    target: str = Field(..., description="Target page node ID")
    label: str = Field(..., description="Edge label describing the action")

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
    pages: List[PageNode] = Field(default_factory=list, description="Extracted page metadata")
    edges: List[Edge] = Field(default_factory=list, description="Edges connecting pages")

class SimplifiedMetadataResponse(BaseModel):
    """Simplified response with only page metadata"""
    pages: List[PageNode] = Field(..., description="Page metadata with key elements")
    edges: List[Edge] = Field(default_factory=list, description="Edges connecting pages")

class ExcelAutomationRequest(BaseModel):
    """Request model for Excel-based complete automation"""
    sheet_name: str = Field(default="Sheet1", description="Name of the Excel sheet to read")
    test_id: Optional[str] = Field(None, description="Specific test ID to execute (if None, executes first test case)")
    browser_type: str = Field(default="chromium", description="Browser type: chromium, firefox, webkit, or edge")
    headless: bool = Field(default=False, description="Run browser in headless mode")
    max_iterations: int = Field(default=10, description="Maximum automation iterations")

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
    log_info("Root endpoint accessed", node="api")
    return {
        "message": "LLMOps Test Case Processing API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint with provider information"""
    log_info("Health check requested", node="api")
    config = get_config()
    provider_info = generator.get_provider_info()
    
    log_info(
        "Health check completed",
        node="api",
        extra={"provider": provider_info["provider"], "model": provider_info["model"]}
    )
    
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
        log_info(
            f"Generating prompt for test case: {request.test_id}",
            node="api.generate_prompt",
            extra={"module": request.module, "functionality": request.functionality}
        )
        
        # Validate input
        if not request.test_id or not request.test_id.strip():
            raise InvalidInputException("test_id is required", field="test_id")
        
        if not request.module or not request.module.strip():
            raise InvalidInputException("module is required", field="module")
        
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
        log_llm("Calling LLM to generate prompt", operation="generate_prompt", model=config.openai_model if not config.use_groq else config.groq_model)
        prompt = generator.generate_playwright_prompt(test_case)
        
        log_prompt(
            "Prompt generated successfully",
            prompt_type="playwright",
            prompt_length=len(prompt.generated_prompt) if prompt.generated_prompt else 0,
            extra={"test_id": request.test_id}
        )
        
        return TestCaseResponse(
            test_id=prompt.test_case.test_id,
            module=prompt.test_case.module,
            functionality=prompt.test_case.functionality,
            description=prompt.test_case.description,
            generated_prompt=prompt.generated_prompt or "",
            generated_at=prompt.generated_at.isoformat() if prompt.generated_at else datetime.now().isoformat()
        )
    
    except InvalidInputException as e:
        log_error(f"Invalid input for prompt generation", error=e)
        raise HTTPException(status_code=400, detail=str(e))
    except LLMException as e:
        log_error(f"LLM error during prompt generation", error=e)
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        log_error(f"Unexpected error generating prompt", error=e)
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


def parse_metadata_from_output(output: str) -> tuple[List[PageNode], List[Edge]]:
    """
    Parse metadata from agent output
    
    Looks for playwright_get_page_metadata tool outputs and structures them
    into PageNode format with ElementMetadata, and extracts edges between pages
    
    Returns:
        tuple: (pages, edges) - List of PageNode objects and list of Edge objects
    """
    import re
    
    pages = []
    edges = []
    page_counter = 1
    
    # Extract all metadata blocks from the output
    # Looking for patterns like:
    # "📄 Page Metadata:\n  • URL: https://example.com\n  • Title: Example Domain"
    # "🎯 Element Metadata (Found 1 element(s)):\n  • Selector: a\n  • Tag: <a>"
    
    # Find page metadata blocks
    page_pattern = r'📄 Page Metadata:\s*\n\s*•\s*URL:\s*([^\n]+)\s*\n\s*•\s*Title:\s*([^\n]+)'
    page_matches = re.finditer(page_pattern, output, re.MULTILINE)
    
    for page_match in page_matches:
        url = page_match.group(1).strip()
        title = page_match.group(2).strip()
        
        # Extract domain for label
        domain_match = re.search(r'https?://([^/]+)', url)
        domain = domain_match.group(1) if domain_match else url
        label = f"{title} ({domain})"
        
        # Find element metadata following this page metadata
        elements = []
        element_counter = 1
        
        # Look for the element metadata block after this page block
        element_pattern = r'🎯 Element Metadata \(Found (\d+) element\(s\)\):(.*?)(?=📄 Page Metadata:|✅ playwright_screenshot|✅ playwright_close|$)'
        element_search_start = page_match.end()
        remaining_output = output[element_search_start:element_search_start + 10000]  # Look ahead 10000 chars
        
        element_match = re.search(element_pattern, remaining_output, re.DOTALL)
        
        if element_match:
            elem_count = int(element_match.group(1))
            elem_block = element_match.group(2)
            
            # Split the element block by "Element X:" pattern to get individual elements
            # Each element section starts with patterns like "Element 1:", "Element 2:", etc.
            individual_element_pattern = r'(?:Element \d+:|•\s*Selector:)'
            element_sections = re.split(individual_element_pattern, elem_block)
            
            # Process each element section
            for section in element_sections:
                if not section.strip():
                    continue
                
                # Extract element attributes from this section
                tag_match = re.search(r'•\s*Tag:\s*<([^>]+)>', section)
                type_match = re.search(r'•\s*Type:\s*([^\n]+)', section)
                text_match = re.search(r'•\s*Text:\s*([^\n]+)', section)
                id_match = re.search(r'•\s*ID:\s*([^\n]+)', section)
                name_match = re.search(r'•\s*Name:\s*([^\n]+)', section)
                class_match = re.search(r'•\s*Class:\s*([^\n]+)', section)
                href_match = re.search(r'•\s*Href:\s*([^\n]+)', section)
                input_type_match = re.search(r'•\s*Input Type:\s*([^\n]+)', section)
                
                # Skip if no tag found (not a valid element section)
                if not tag_match:
                    continue
                
                tag = tag_match.group(1).strip()
                element_type = type_match.group(1).strip() if type_match else tag
                
                # Determine element type from tag if not specified
                if element_type == tag:
                    if tag == "a":
                        element_type = "link"
                    elif tag == "button":
                        element_type = "button"
                    elif tag == "input":
                        element_type = "input"
                    elif tag == "form":
                        element_type = "form"
                
                element = ElementMetadata(
                    id=f"element_{element_counter}",
                    type=element_type,
                    tag=tag,
                    text=text_match.group(1).strip() if text_match and text_match.group(1).strip() not in ["None", "null", ""] else None,
                    element_id=id_match.group(1).strip() if id_match and id_match.group(1).strip() not in ["None", "null", ""] else None,
                    name=name_match.group(1).strip() if name_match and name_match.group(1).strip() not in ["None", "null", ""] else None,
                    class_name=class_match.group(1).strip() if class_match and class_match.group(1).strip() not in ["None", "null", ""] else None,
                    href=href_match.group(1).strip() if href_match and href_match.group(1).strip() not in ["None", "null", ""] else None,
                    input_type=input_type_match.group(1).strip() if input_type_match and input_type_match.group(1).strip() not in ["None", "null", ""] else None,
                    depends_on=[]
                )
                
                elements.append(element)
                element_counter += 1
        
        # Create page node
        page_node = PageNode(
            id=f"page_{page_counter}",
            label=label,
            x=200 + (page_counter - 1) * 300,  # Offset pages horizontally
            y=100,
            metadata=PageMetadata(
                url=url,
                title=title,
                key_elements=elements
            )
        )
        
        pages.append(page_node)
        page_counter += 1
    
    # Extract edges from navigation actions
    # Look for patterns like "✅ playwright_click: ✅ Clicked on element: <text>"
    # followed by navigation to a new page
    click_pattern = r'✅ playwright_click:.*?(?:Clicked|Click).*?[:\s]+([^\n]{0,50}?)(?:\n|$)'
    click_matches = list(re.finditer(click_pattern, output, re.IGNORECASE))
    
    # Create edges between consecutive pages based on click actions
    for i in range(len(pages) - 1):
        source_id = pages[i].id
        target_id = pages[i + 1].id
        
        # Try to find the click action between these pages
        edge_label = "Navigate"
        
        # Look for click action text near this page transition
        if i < len(click_matches):
            click_text = click_matches[i].group(1).strip()
            # Truncate long text
            if len(click_text) > 25:
                click_text = click_text[:22] + "..."
            edge_label = f"Click {click_text}" if click_text else "Click"
        
        edges.append(Edge(
            source=source_id,
            target=target_id,
            label=edge_label
        ))
    
    return pages, edges


@app.post("/execute-playwright", response_model=PlaywrightExecutionResponse, tags=["Playwright Automation"])
async def execute_playwright_automation(request: PlaywrightExecutionRequest):
    """
    Execute Playwright automation based on generated prompt
    
    This endpoint takes the output from /generate-prompt and executes
    the automated test using Playwright agent.
    
    Args:
        request: Contains test_id, generated_prompt, and browser settings
    
    Returns:
        Execution results with status, steps, screenshots, and extracted metadata
    
    Example workflow:
        1. POST /generate-prompt -> Get generated_prompt
        2. POST /execute-playwright -> Execute automation with the prompt
    """
    import time
    import re
    
    try:
        # Validate input
        if not request.test_id or not request.test_id.strip():
            raise InvalidInputException("test_id is required", field="test_id")
        
        if not request.generated_prompt or not request.generated_prompt.strip():
            raise InvalidInputException("generated_prompt is required", field="generated_prompt")
        
        log_info(
            f"Starting Playwright automation for test: {request.test_id}",
            node="api.execute_playwright",
            extra={
                "browser_type": request.browser_type,
                "headless": request.headless,
                "max_iterations": request.max_iterations
            }
        )
        
        start_time = time.time()
        
        # Initialize Playwright Agent
        # Get custom OpenAI config from environment
        api_key = os.getenv("CUSTOM_OPENAI_KEY")
        gateway_url = os.getenv("CUSTOM_OPENAI_GATEWAY_URL")
        
        # Initialize Playwright Agent with OpenAI or Groq
        # Auto-detect provider from config (USE_GROQ env variable)
        log_info("Initializing Playwright Agent", node="playwright")
        agent = PlaywrightAgent(config=config)
        
        # Execute the automation with the generated prompt
        log_info(f"Executing automation with prompt length: {len(request.generated_prompt)}", node="playwright")
        result = await agent.run(
            test_prompt=request.generated_prompt,
            max_iterations=request.max_iterations,
            browser_config={"browser_type": request.browser_type, "headless": request.headless}
        )
        
        log_info(
            f"Using browser type from request: {request.browser_type}",
            node="playwright",
            extra={"browser_type": request.browser_type}
        )
        
        execution_time = time.time() - start_time
        log_info(
            f"Playwright execution completed in {execution_time:.2f}s",
            node="playwright",
            extra={"test_id": request.test_id, "execution_time": execution_time}
        )
        
        # Parse the result to extract useful information
        agent_output = str(result) if result else "No output"
        
        # Get the final response which contains tool execution results
        final_response = result.get("final_response", "") if isinstance(result, dict) else ""
        
        # Count steps executed (messages in the conversation)
        steps_executed = len(result.get("messages", [])) if isinstance(result, dict) else 0
        
        # Check if automation completed successfully
        # Consider it successful if browser navigation occurred and no errors
        is_success = "error" not in agent_output.lower() and "failed" not in agent_output.lower()
        status = "success" if is_success else "failed"
        
        # Look for screenshot mentions in output
        screenshots = []
        screenshot_matches = re.findall(r'screenshot.*?([a-zA-Z0-9_-]+\.png)', final_response, re.IGNORECASE)
        screenshots.extend(screenshot_matches)
        
        # Parse metadata from the final response which contains tool execution results
        log_info("Parsing metadata from execution results", node="playwright")
        pages, edges = parse_metadata_from_output(final_response)
        
        log_info(
            f"Automation {status} - Extracted {len(pages)} pages and {len(edges)} edges",
            node="playwright",
            extra={"test_id": request.test_id, "status": status, "screenshots": len(screenshots)}
        )
        
        return PlaywrightExecutionResponse(
            test_id=request.test_id,
            status=status,
            execution_time=round(execution_time, 2),
            steps_executed=steps_executed,
            agent_output=agent_output,
            screenshots=screenshots,
            error_message=None if is_success else "Automation encountered issues. Check agent_output for details.",
            executed_at=datetime.now().isoformat(),
            pages=pages,
            edges=edges
        )
        
    except InvalidInputException as e:
        log_error(f"Invalid input for Playwright execution", error=e)
        raise HTTPException(status_code=400, detail=str(e))
    except PlaywrightException as e:
        log_error(
            f"Playwright browser error for test: {request.test_id}",
            error=e,
            extra={"test_id": request.test_id}
        )
        execution_time = time.time() - start_time
        return PlaywrightExecutionResponse(
            test_id=request.test_id,
            status="error",
            execution_time=round(execution_time, 2),
            steps_executed=0,
            agent_output="",
            screenshots=[],
            error_message=str(e),
            executed_at=datetime.now().isoformat(),
            pages=[],
            edges=[]
        )
    except StateException as e:
        log_error(
            f"Playwright state error for test: {request.test_id}",
            error=e,
            extra={"test_id": request.test_id}
        )
        execution_time = time.time() - start_time
        return PlaywrightExecutionResponse(
            test_id=request.test_id,
            status="error",
            execution_time=round(execution_time, 2),
            steps_executed=0,
            agent_output="",
            screenshots=[],
            error_message=str(e),
            executed_at=datetime.now().isoformat(),
            pages=[],
            edges=[]
        )
    except Exception as e:
        log_error(
            f"Unexpected error during Playwright automation for test: {request.test_id}",
            error=e,
            extra={"test_id": request.test_id}
        )
        execution_time = time.time() - start_time
        return PlaywrightExecutionResponse(
            test_id=request.test_id,
            status="error",
            execution_time=round(execution_time, 2),
            steps_executed=0,
            agent_output="",
            screenshots=[],
            error_message=str(e),
            executed_at=datetime.now().isoformat(),
            pages=[],
            edges=[]
        )


@app.post("/execute-playwright-metadata", response_model=SimplifiedMetadataResponse, tags=["Playwright Automation"])
async def execute_playwright_get_metadata(request: PlaywrightExecutionRequest):
    """
    Execute Playwright automation and return ONLY the structured page metadata
    
    This endpoint is like /execute-playwright but returns only the clean,
    structured metadata without verbose agent logs.
    
    Args:
        request: Contains test_id, generated_prompt, and browser settings
    
    Returns:
        Only the pages array with structured metadata (id, label, x, y, metadata)
    
    Example Response:
    {
        "pages": [
            {
                "id": "page_1",
                "label": "Example Domain (example.com)",
                "x": 200,
                "y": 100,
                "metadata": {
                    "url": "https://example.com/",
                    "title": "Example Domain",
                    "key_elements": [
                        {
                            "id": "element_1",
                            "type": "link",
                            "tag": "a",
                            "text": "More information...",
                            ...
                        }
                    ]
                }
            }
        ]
    }
    """
    # Call the full execution endpoint
    full_response = await execute_playwright_automation(request)
    
    # Return only the pages and edges data
    return SimplifiedMetadataResponse(pages=full_response.pages, edges=full_response.edges)


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
            browser_type=request.browser_type,  # Use browser_type from test case
            headless=False,
            max_iterations=10
        )
        
        return await execute_playwright_automation(exec_request)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in combined execution: {str(e)}")


@app.post("/execute-from-excel", response_model=SimplifiedMetadataResponse, tags=["Complete Automation"])
async def execute_complete_automation_from_excel(
    file: UploadFile = File(..., description="Excel file with test cases"),
    sheet_name: str = "Sheet1",
    test_id: Optional[str] = None,
    browser_type: str = "chromium",
    headless: bool = False,
    max_iterations: int = 10
):
    """
    🎯 FINAL COMBINED ENDPOINT - Complete End-to-End Automation
    
    This endpoint performs ALL steps in one call:
    1. ✅ Read Excel file with test cases
    2. ✅ Generate Playwright prompt from test case
    3. ✅ Execute Playwright automation
    4. ✅ Extract structured JSON with nodes and edges
    
    Args:
        file: Excel file containing test cases
        sheet_name: Name of the sheet to read (default: "Sheet1")
        test_id: Specific test ID to execute (if None, uses first test case)
        browser_type: Browser to use - chromium, firefox, webkit, or edge (default: "chromium")
        headless: Run browser in headless mode (default: False)
        max_iterations: Maximum automation iterations (default: 10)
    
    Returns:
        SimplifiedMetadataResponse with:
        - pages: Array of page nodes with structured metadata
        - edges: Array of edges connecting pages
    
    Example Response:
    {
        "pages": [
            {
                "id": "page_1",
                "label": "Example Domain (example.com)",
                "x": 200,
                "y": 100,
                "metadata": {
                    "url": "https://example.com/",
                    "title": "Example Domain",
                    "key_elements": [...]
                }
            }
        ],
        "edges": [
            {
                "source": "page_1",
                "target": "page_2",
                "label": "Navigate to About"
            }
        ]
    }
    
    Usage:
        curl -X POST "http://localhost:8000/execute-from-excel" \\
             -F "file=@test_cases.xlsx" \\
             -F "sheet_name=Sheet1" \\
             -F "browser_type=edge" \\
             -F "headless=false"
    """
    log_info(
        "Starting complete automation from Excel",
        node="complete_automation",
        extra={
            "filename": file.filename,
            "sheet_name": sheet_name,
            "test_id": test_id,
            "browser_type": browser_type,
            "headless": headless
        }
    )
    
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be an Excel file (.xlsx or .xls)")
    
    tmp_path = None
    try:
        # Step 1: Save uploaded Excel file to temp location
        log_info("Step 1: Saving Excel file", node="complete_automation.step1")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        # Step 2: Read test cases from Excel
        log_info("Step 2: Reading test cases from Excel", node="complete_automation.step2")
        test_cases = generator.read_test_cases(tmp_path, sheet_name=sheet_name)
        
        if not test_cases:
            raise HTTPException(status_code=404, detail="No test cases found in Excel file")
        
        log_info(
            f"Found {len(test_cases)} test cases in Excel",
            node="complete_automation.step2",
            extra={"total_test_cases": len(test_cases)}
        )
        
        # Step 3: Select test case to execute
        selected_test_case = None
        if test_id:
            # Find specific test case by ID
            for tc in test_cases:
                if tc.test_id == test_id:
                    selected_test_case = tc
                    break
            if not selected_test_case:
                raise HTTPException(status_code=404, detail=f"Test case with ID '{test_id}' not found")
            log_info(f"Step 3: Selected test case by ID: {test_id}", node="complete_automation.step3")
        else:
            # Use first test case
            selected_test_case = test_cases[0]
            log_info(f"Step 3: Using first test case: {selected_test_case.test_id}", node="complete_automation.step3")
        
        # Step 4: Generate Playwright prompt
        log_info(f"Step 4: Generating Playwright prompt for {selected_test_case.test_id}", node="complete_automation.step4")
        prompt_result = generator.generate_playwright_prompt(selected_test_case)
        generated_prompt = prompt_result.generated_prompt
        
        if not generated_prompt:
            raise HTTPException(status_code=500, detail="Failed to generate Playwright prompt")
        
        log_info(
            f"Prompt generated successfully (length: {len(generated_prompt)})",
            node="complete_automation.step4",
            extra={"prompt_length": len(generated_prompt)}
        )
        
        # Step 5: Execute Playwright automation
        log_info(f"Step 5: Executing Playwright automation with {browser_type} browser", node="complete_automation.step5")
        exec_request = PlaywrightExecutionRequest(
            test_id=selected_test_case.test_id,
            generated_prompt=generated_prompt,
            browser_type=browser_type,
            headless=headless,
            max_iterations=max_iterations
        )
        
        full_response = await execute_playwright_automation(exec_request)
        
        # Step 6: Extract and return structured JSON with nodes and edges
        log_info("Step 6: Extracting structured metadata (nodes and edges)", node="complete_automation.step6")
        result = SimplifiedMetadataResponse(
            pages=full_response.pages,
            edges=full_response.edges
        )
        
        log_info(
            "Complete automation finished successfully",
            node="complete_automation.success",
            extra={
                "test_id": selected_test_case.test_id,
                "pages_extracted": len(result.pages),
                "edges_extracted": len(result.edges),
                "execution_time": full_response.execution_time
            }
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(
            "Error in complete automation from Excel",
            error=e,
            extra={"filename": file.filename, "test_id": test_id}
        )
        raise HTTPException(status_code=500, detail=f"Error in complete automation: {str(e)}")
    
    finally:
        # Clean up temp file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
                log_info("Cleaned up temporary Excel file", node="complete_automation.cleanup")
            except Exception as e:
                log_error("Failed to clean up temp file", error=e)


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
    
    # Log startup information
    log_info(
        "Starting LLMOps API Server",
        node="startup",
        extra={
            "app_env": config.app_env,
            "provider": provider_info['provider'],
            "model": provider_info['model'],
            "browser_type": config.browser_type
        }
    )
    
    print("\n" + "=" * 70)
    print("Starting server on http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("=" * 70 + "\n")
    
    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000)
