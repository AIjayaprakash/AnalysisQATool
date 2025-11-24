"""
Logger Module

This module provides logging functionality for the application. 
It includes configuration for logging to console and file, as well as 
integration with external logging services if enabled.

Functions:
    get_logger: Initializes and returns a configured logger instance.
    log_info: Logs informational messages, with optional node context.
    log_warning: Logs warning messages.
    log_error: Logs error messages.
    log_debug: Logs debug messages.
    log_llm: Logs messages related to LLM operations.
    log_langfuse: Logs messages related to Langfuse integration.
    log_db: Logs database related messages.
    log_prompt: Logs prompt related messages.

Usage:
    Import the module and use the provided logging functions to log messages 
    throughout the application.
    
    Example:
        from llmops.common.logger import log_info, log_error, get_logger
        
        logger = get_logger(__name__)
        log_info("Application started", node="main")
        log_error("Failed to connect", error=exception)
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Any, Dict
from datetime import datetime
import json

# Global logger instances cache
_loggers: Dict[str, logging.Logger] = {}

# Default log format
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DETAILED_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

# Log file configuration
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


class CustomFormatter(logging.Formatter):
    """Custom formatter with color support for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        # Format the message
        result = super().format(record)
        
        # Reset levelname for file logging
        record.levelname = levelname
        
        return result


def get_logger(
    name: str,
    level: int = logging.INFO,
    log_to_file: bool = True,
    log_to_console: bool = True,
    use_colors: bool = True
) -> logging.Logger:
    """
    Initialize and return a configured logger instance.
    
    Args:
        name: Name of the logger (typically __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
        use_colors: Whether to use colored output in console
        
    Returns:
        Configured logger instance
        
    Example:
        logger = get_logger(__name__)
        logger.info("Application started")
    """
    # Return cached logger if exists
    if name in _loggers:
        return _loggers[name]
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        if use_colors:
            console_formatter = CustomFormatter(DEFAULT_FORMAT)
        else:
            console_formatter = logging.Formatter(DEFAULT_FORMAT)
        
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_to_file:
        # Create dated log file
        log_file = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}_app.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        
        file_formatter = logging.Formatter(DETAILED_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Cache the logger
    _loggers[name] = logger
    
    return logger


def log_info(
    message: str,
    logger_name: str = "app",
    node: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log informational messages, with optional node context.
    
    Args:
        message: The message to log
        logger_name: Name of the logger to use
        node: Optional node/module context (e.g., "playwright_agent", "api")
        extra: Optional dictionary of extra data to log
        
    Example:
        log_info("Processing started", node="data_processor")
        log_info("User logged in", node="auth", extra={"user_id": 123})
    """
    logger = get_logger(logger_name)
    
    if node:
        message = f"[{node}] {message}"
    
    if extra:
        message = f"{message} | Extra: {json.dumps(extra)}"
    
    logger.info(message)


def log_warning(
    message: str,
    logger_name: str = "app",
    extra: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log warning messages.
    
    Args:
        message: The warning message to log
        logger_name: Name of the logger to use
        extra: Optional dictionary of extra data to log
        
    Example:
        log_warning("API rate limit approaching")
        log_warning("Deprecated function called", extra={"function": "old_method"})
    """
    logger = get_logger(logger_name)
    
    if extra:
        message = f"{message} | Extra: {json.dumps(extra)}"
    
    logger.warning(message)


def log_error(
    message: str,
    logger_name: str = "app",
    error: Optional[Exception] = None,
    extra: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log error messages.
    
    Args:
        message: The error message to log
        logger_name: Name of the logger to use
        error: Optional exception object
        extra: Optional dictionary of extra data to log
        
    Example:
        log_error("Database connection failed")
        log_error("Failed to process", error=exception, extra={"file": "data.csv"})
    """
    logger = get_logger(logger_name)
    
    if error:
        message = f"{message} | Error: {str(error)}"
    
    if extra:
        message = f"{message} | Extra: {json.dumps(extra)}"
    
    logger.error(message, exc_info=error is not None)


def log_debug(
    message: str,
    logger_name: str = "app",
    extra: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log debug messages.
    
    Args:
        message: The debug message to log
        logger_name: Name of the logger to use
        extra: Optional dictionary of extra data to log
        
    Example:
        log_debug("Variable value check", extra={"var": value})
        log_debug("Function entry point")
    """
    logger = get_logger(logger_name)
    
    if extra:
        message = f"{message} | Extra: {json.dumps(extra)}"
    
    logger.debug(message)


def log_llm(
    message: str,
    operation: Optional[str] = None,
    model: Optional[str] = None,
    tokens: Optional[int] = None,
    extra: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log messages related to LLM operations.
    
    Args:
        message: The message to log
        operation: Type of LLM operation (e.g., "completion", "embedding")
        model: Model name used
        tokens: Number of tokens used
        extra: Optional dictionary of extra data to log
        
    Example:
        log_llm("Generated response", operation="completion", model="gpt-4o", tokens=150)
        log_llm("Prompt sent", operation="chat", extra={"prompt_length": 100})
    """
    logger = get_logger("llm")
    
    context_parts = []
    if operation:
        context_parts.append(f"op={operation}")
    if model:
        context_parts.append(f"model={model}")
    if tokens:
        context_parts.append(f"tokens={tokens}")
    
    context = " | ".join(context_parts)
    if context:
        message = f"[LLM] {message} | {context}"
    else:
        message = f"[LLM] {message}"
    
    if extra:
        message = f"{message} | Extra: {json.dumps(extra)}"
    
    logger.info(message)


def log_langfuse(
    message: str,
    trace_id: Optional[str] = None,
    span_id: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log messages related to Langfuse integration.
    
    Args:
        message: The message to log
        trace_id: Optional Langfuse trace ID
        span_id: Optional Langfuse span ID
        extra: Optional dictionary of extra data to log
        
    Example:
        log_langfuse("Trace started", trace_id="abc123")
        log_langfuse("Span completed", trace_id="abc123", span_id="def456")
    """
    logger = get_logger("langfuse")
    
    context_parts = []
    if trace_id:
        context_parts.append(f"trace={trace_id}")
    if span_id:
        context_parts.append(f"span={span_id}")
    
    context = " | ".join(context_parts)
    if context:
        message = f"[Langfuse] {message} | {context}"
    else:
        message = f"[Langfuse] {message}"
    
    if extra:
        message = f"{message} | Extra: {json.dumps(extra)}"
    
    logger.info(message)


def log_db(
    message: str,
    operation: Optional[str] = None,
    table: Optional[str] = None,
    rows_affected: Optional[int] = None,
    extra: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log database related messages.
    
    Args:
        message: The message to log
        operation: Database operation type (e.g., "SELECT", "INSERT", "UPDATE")
        table: Table name
        rows_affected: Number of rows affected
        extra: Optional dictionary of extra data to log
        
    Example:
        log_db("Query executed", operation="SELECT", table="users")
        log_db("Records updated", operation="UPDATE", table="orders", rows_affected=5)
    """
    logger = get_logger("database")
    
    context_parts = []
    if operation:
        context_parts.append(f"op={operation}")
    if table:
        context_parts.append(f"table={table}")
    if rows_affected is not None:
        context_parts.append(f"rows={rows_affected}")
    
    context = " | ".join(context_parts)
    if context:
        message = f"[DB] {message} | {context}"
    else:
        message = f"[DB] {message}"
    
    if extra:
        message = f"{message} | Extra: {json.dumps(extra)}"
    
    logger.info(message)


def log_prompt(
    message: str,
    prompt_type: Optional[str] = None,
    prompt_length: Optional[int] = None,
    template: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log prompt related messages.
    
    Args:
        message: The message to log
        prompt_type: Type of prompt (e.g., "system", "user", "assistant")
        prompt_length: Length of the prompt in characters
        template: Template name or ID used
        extra: Optional dictionary of extra data to log
        
    Example:
        log_prompt("Generated prompt", prompt_type="system", prompt_length=200)
        log_prompt("Template applied", template="test_case_template")
    """
    logger = get_logger("prompt")
    
    context_parts = []
    if prompt_type:
        context_parts.append(f"type={prompt_type}")
    if prompt_length is not None:
        context_parts.append(f"length={prompt_length}")
    if template:
        context_parts.append(f"template={template}")
    
    context = " | ".join(context_parts)
    if context:
        message = f"[Prompt] {message} | {context}"
    else:
        message = f"[Prompt] {message}"
    
    if extra:
        message = f"{message} | Extra: {json.dumps(extra)}"
    
    logger.info(message)


# Initialize default logger
default_logger = get_logger("app")


if __name__ == "__main__":
    # Test all logging functions
    print("=" * 80)
    print("Testing Logger Module")
    print("=" * 80)
    
    log_info("Application started", node="main")
    log_debug("Debug information", extra={"debug_var": 123})
    log_warning("This is a warning message")
    
    try:
        raise ValueError("Test error")
    except ValueError as e:
        log_error("An error occurred", error=e, extra={"context": "test"})
    
    log_llm("LLM request", operation="completion", model="gpt-4o", tokens=150)
    log_langfuse("Langfuse trace", trace_id="trace123", span_id="span456")
    log_db("Database query", operation="SELECT", table="users", rows_affected=10)
    log_prompt("Prompt generated", prompt_type="system", prompt_length=200, template="test_template")
    
    print("\n" + "=" * 80)
    print("Logger test complete! Check logs/ directory for log files.")
    print("=" * 80)
