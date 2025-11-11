@echo off
REM Start LLMOps FastAPI Server

echo ======================================================================
echo LLMOps FastAPI Server Startup
echo ======================================================================
echo.

REM Check if environment variables are set
if "%USE_GROQ%"=="" (
    echo WARNING: USE_GROQ not set. Using default configuration.
) else (
    echo ✓ USE_GROQ = %USE_GROQ%
)

if "%GROQ_API_KEY%"=="" (
    if "%USE_GROQ%"=="true" (
        echo WARNING: GROQ_API_KEY not set but USE_GROQ=true
    )
) else (
    echo ✓ GROQ_API_KEY = ********
)

if "%CUSTOM_OPENAI_KEY%"=="" (
    if NOT "%USE_GROQ%"=="true" (
        echo WARNING: CUSTOM_OPENAI_KEY not set but USE_GROQ=false
    )
) else (
    echo ✓ CUSTOM_OPENAI_KEY = ********
)

echo.
echo ======================================================================
echo Starting API Server...
echo ======================================================================
echo.
echo API will be available at:
echo   - Main API: http://localhost:8000
echo   - Swagger UI: http://localhost:8000/docs
echo   - ReDoc: http://localhost:8000/redoc
echo.
echo Press Ctrl+C to stop the server
echo ======================================================================
echo.

python llmops_api.py
