"""
Custom Exception Classes

This module defines custom exception classes for the application. 
These modules can be used to handle specific error scenarios related to 
the pipeline and validation processes.
"""

from typing import Optional, Dict, Any


class StateException(Exception):
    """
    Base exception for pipeline-related errors.
    
    This exception is raised when there are issues with the pipeline state
    or workflow execution.
    
    Args:
        message: The error message
        state: Optional dictionary containing state information
        
    Example:
        raise StateException("Invalid pipeline state", state={"step": "validation"})
    """
    
    def __init__(self, message: str, state: Optional[Dict[str, Any]] = None):
        self.message = message
        self.state = state or {}
        super().__init__(self.message)
    
    def __str__(self):
        if self.state:
            return f"{self.message} | State: {self.state}"
        return self.message


class InvalidInputException(Exception):
    """
    Exception raised for invalid input.
    
    This exception is raised when input data does not meet the expected
    format, type, or validation criteria.
    
    Args:
        message: The error message
        input_data: Optional dictionary containing the invalid input
        field: Optional field name that caused the error
        
    Example:
        raise InvalidInputException("Invalid email format", field="email")
    """
    
    def __init__(
        self, 
        message: str, 
        input_data: Optional[Any] = None,
        field: Optional[str] = None
    ):
        self.message = message
        self.input_data = input_data
        self.field = field
        super().__init__(self.message)
    
    def __str__(self):
        parts = [self.message]
        if self.field:
            parts.append(f"Field: {self.field}")
        if self.input_data is not None:
            parts.append(f"Input: {self.input_data}")
        return " | ".join(parts)


class AuthorizationException(Exception):
    """
    Exception raised for authorization errors.
    
    This exception is raised when a user or service lacks the necessary
    permissions or credentials to perform an action.
    
    Args:
        message: The error message
        user: Optional user identifier
        resource: Optional resource being accessed
        
    Example:
        raise AuthorizationException("Access denied", user="user123", resource="admin_panel")
    """
    
    def __init__(
        self,
        message: str,
        user: Optional[str] = None,
        resource: Optional[str] = None
    ):
        self.message = message
        self.user = user
        self.resource = resource
        super().__init__(self.message)
    
    def __str__(self):
        parts = [self.message]
        if self.user:
            parts.append(f"User: {self.user}")
        if self.resource:
            parts.append(f"Resource: {self.resource}")
        return " | ".join(parts)


class InvalidTextException(Exception):
    """
    Exception raised for invalid text input.
    
    This exception is raised when text input does not meet requirements
    such as length, format, encoding, or content validation.
    
    Args:
        message: The error message
        text: Optional text that caused the error
        reason: Optional reason for invalidity
        
    Example:
        raise InvalidTextException("Text too long", text=long_text[:50], reason="max_length_exceeded")
    """
    
    def __init__(
        self,
        message: str,
        text: Optional[str] = None,
        reason: Optional[str] = None
    ):
        self.message = message
        self.text = text
        self.reason = reason
        super().__init__(self.message)
    
    def __str__(self):
        parts = [self.message]
        if self.reason:
            parts.append(f"Reason: {self.reason}")
        if self.text:
            # Truncate long text for display
            display_text = self.text[:100] + "..." if len(self.text) > 100 else self.text
            parts.append(f"Text: {display_text}")
        return " | ".join(parts)


class ValidationException(Exception):
    """
    Exception raised for validation-related errors.
    
    This exception is raised when data validation fails, including
    schema validation, business rule validation, or constraint violations.
    
    Args:
        message: The error message
        errors: Optional dictionary of validation errors by field
        data: Optional data that failed validation
        
    Example:
        raise ValidationException(
            "Validation failed", 
            errors={"email": "Invalid format", "age": "Must be positive"}
        )
    """
    
    def __init__(
        self,
        message: str,
        errors: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.errors = errors or {}
        self.data = data or {}
        super().__init__(self.message)
    
    def __str__(self):
        parts = [self.message]
        if self.errors:
            error_str = ", ".join([f"{k}: {v}" for k, v in self.errors.items()])
            parts.append(f"Errors: {error_str}")
        return " | ".join(parts)
    
    def get_errors(self) -> Dict[str, str]:
        """Get validation errors as dictionary"""
        return self.errors
    
    def has_errors(self) -> bool:
        """Check if there are validation errors"""
        return len(self.errors) > 0


# Additional helper exceptions for specific scenarios

class PipelineStateException(StateException):
    """
    Exception for pipeline state-specific errors.
    
    Inherits from StateException but provides more specific context
    for pipeline execution issues.
    """
    pass


class ConfigurationException(Exception):
    """
    Exception raised for configuration errors.
    
    This exception is raised when there are issues with application
    configuration, environment variables, or settings.
    
    Args:
        message: The error message
        config_key: Optional configuration key that caused the error
        
    Example:
        raise ConfigurationException("Missing API key", config_key="OPENAI_API_KEY")
    """
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        self.message = message
        self.config_key = config_key
        super().__init__(self.message)
    
    def __str__(self):
        if self.config_key:
            return f"{self.message} | Config Key: {self.config_key}"
        return self.message


class LLMException(Exception):
    """
    Exception raised for LLM-related errors.
    
    This exception is raised when there are issues with LLM operations
    such as API calls, rate limits, or response parsing.
    
    Args:
        message: The error message
        provider: Optional LLM provider name
        model: Optional model name
        
    Example:
        raise LLMException("Rate limit exceeded", provider="openai", model="gpt-4o")
    """
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.message = message
        self.provider = provider
        self.model = model
        super().__init__(self.message)
    
    def __str__(self):
        parts = [self.message]
        if self.provider:
            parts.append(f"Provider: {self.provider}")
        if self.model:
            parts.append(f"Model: {self.model}")
        return " | ".join(parts)


class DatabaseException(Exception):
    """
    Exception raised for database-related errors.
    
    This exception is raised when there are database connection,
    query, or data integrity issues.
    
    Args:
        message: The error message
        operation: Optional database operation
        table: Optional table name
        
    Example:
        raise DatabaseException("Connection failed", operation="INSERT", table="users")
    """
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None
    ):
        self.message = message
        self.operation = operation
        self.table = table
        super().__init__(self.message)
    
    def __str__(self):
        parts = [self.message]
        if self.operation:
            parts.append(f"Operation: {self.operation}")
        if self.table:
            parts.append(f"Table: {self.table}")
        return " | ".join(parts)


class PlaywrightException(Exception):
    """
    Exception raised for Playwright automation errors.
    
    This exception is raised when there are issues with browser
    automation, element selection, or navigation.
    
    Args:
        message: The error message
        action: Optional action being performed
        selector: Optional element selector
        
    Example:
        raise PlaywrightException("Element not found", action="click", selector="#submit-btn")
    """
    
    def __init__(
        self,
        message: str,
        action: Optional[str] = None,
        selector: Optional[str] = None
    ):
        self.message = message
        self.action = action
        self.selector = selector
        super().__init__(self.message)
    
    def __str__(self):
        parts = [self.message]
        if self.action:
            parts.append(f"Action: {self.action}")
        if self.selector:
            parts.append(f"Selector: {self.selector}")
        return " | ".join(parts)


# Exception mapping for easy lookup
EXCEPTION_MAP = {
    "state": StateException,
    "invalid_input": InvalidInputException,
    "authorization": AuthorizationException,
    "invalid_text": InvalidTextException,
    "validation": ValidationException,
    "pipeline_state": PipelineStateException,
    "configuration": ConfigurationException,
    "llm": LLMException,
    "database": DatabaseException,
    "playwright": PlaywrightException
}


def get_exception_class(exception_type: str) -> type:
    """
    Get exception class by type name.
    
    Args:
        exception_type: Type of exception
        
    Returns:
        Exception class
        
    Example:
        exc_class = get_exception_class("validation")
        raise exc_class("Validation failed")
    """
    return EXCEPTION_MAP.get(exception_type, Exception)


if __name__ == "__main__":
    # Test all exception classes
    print("=" * 80)
    print("Testing Custom Exception Classes")
    print("=" * 80)
    
    # Test StateException
    try:
        raise StateException("Pipeline failed", state={"step": "validation", "status": "error"})
    except StateException as e:
        print(f"\n✓ StateException: {e}")
    
    # Test InvalidInputException
    try:
        raise InvalidInputException("Invalid email format", field="email", input_data="invalid@")
    except InvalidInputException as e:
        print(f"✓ InvalidInputException: {e}")
    
    # Test AuthorizationException
    try:
        raise AuthorizationException("Access denied", user="user123", resource="admin_panel")
    except AuthorizationException as e:
        print(f"✓ AuthorizationException: {e}")
    
    # Test InvalidTextException
    try:
        raise InvalidTextException("Text too long", text="Very long text" * 20, reason="max_length_exceeded")
    except InvalidTextException as e:
        print(f"✓ InvalidTextException: {e}")
    
    # Test ValidationException
    try:
        raise ValidationException(
            "Validation failed",
            errors={"email": "Invalid format", "age": "Must be positive"}
        )
    except ValidationException as e:
        print(f"✓ ValidationException: {e}")
        print(f"  Has errors: {e.has_errors()}")
        print(f"  Errors: {e.get_errors()}")
    
    # Test ConfigurationException
    try:
        raise ConfigurationException("Missing API key", config_key="OPENAI_API_KEY")
    except ConfigurationException as e:
        print(f"✓ ConfigurationException: {e}")
    
    # Test LLMException
    try:
        raise LLMException("Rate limit exceeded", provider="openai", model="gpt-4o")
    except LLMException as e:
        print(f"✓ LLMException: {e}")
    
    # Test DatabaseException
    try:
        raise DatabaseException("Connection failed", operation="INSERT", table="users")
    except DatabaseException as e:
        print(f"✓ DatabaseException: {e}")
    
    # Test PlaywrightException
    try:
        raise PlaywrightException("Element not found", action="click", selector="#submit-btn")
    except PlaywrightException as e:
        print(f"✓ PlaywrightException: {e}")
    
    print("\n" + "=" * 80)
    print("All exception classes tested successfully!")
    print("=" * 80)
