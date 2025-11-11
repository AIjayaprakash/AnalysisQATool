"""Data models and schemas for test case processing"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime


class TestCaseStatus(Enum):
    """Status of test case execution"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TestCase:
    """Represents a test case from Excel"""
    test_id: str
    module: str
    functionality: str
    description: str
    steps: Optional[str] = None
    expected_result: Optional[str] = None
    test_data: Optional[Dict[str, Any]] = None
    priority: str = "Medium"
    status: TestCaseStatus = TestCaseStatus.PENDING
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert test case to dictionary"""
        return {
            "test_id": self.test_id,
            "module": self.module,
            "functionality": self.functionality,
            "description": self.description,
            "steps": self.steps,
            "expected_result": self.expected_result,
            "test_data": self.test_data,
            "priority": self.priority,
            "status": self.status.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestCase":
        """Create test case from dictionary"""
        status = data.get("status", "pending")
        if isinstance(status, str):
            status = TestCaseStatus(status)
        
        return cls(
            test_id=data.get("test_id", ""),
            module=data.get("module", ""),
            functionality=data.get("functionality", ""),
            description=data.get("description", ""),
            steps=data.get("steps"),
            expected_result=data.get("expected_result"),
            test_data=data.get("test_data"),
            priority=data.get("priority", "Medium"),
            status=status
        )


@dataclass
class TestCasePrompt:
    """Represents a generated Playwright prompt for a test case"""
    test_case: TestCase
    system_prompt: str
    user_prompt: str
    generated_prompt: Optional[str] = None
    generated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "test_case": self.test_case.to_dict(),
            "system_prompt": self.system_prompt,
            "user_prompt": self.user_prompt,
            "generated_prompt": self.generated_prompt,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None
        }


@dataclass
class ExecutionResult:
    """Result of test case execution"""
    test_case: TestCase
    status: TestCaseStatus
    execution_time: float
    error_message: Optional[str] = None
    screenshots: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    executed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "test_case": self.test_case.to_dict(),
            "status": self.status.value,
            "execution_time": self.execution_time,
            "error_message": self.error_message,
            "screenshots": self.screenshots,
            "logs": self.logs,
            "executed_at": self.executed_at.isoformat()
        }
    
    @property
    def passed(self) -> bool:
        """Check if test passed"""
        return self.status == TestCaseStatus.PASSED
    
    @property
    def failed(self) -> bool:
        """Check if test failed"""
        return self.status == TestCaseStatus.FAILED
