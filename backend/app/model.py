from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class ElementNode(BaseModel):
    id: str
    label: Optional[str] = None
    type: Optional[str] = None
    attributes: Dict[str, Any] = {}
    position: Dict[str, int] = {}

class Edge(BaseModel):
    id: str
    source: str
    target: str
    action: Optional[str] = None
    description: Optional[str] = None

class TestRunRequest(BaseModel):
    test_case: str
    test_scenario: str
    url: str
    # For this scaffolding, test_steps is an array of actions that the runner will perform:
    # [{"selector": "#username", "action": "send_keys", "value":"user1"}, {"selector":"#login","action":"click"}]
    test_steps: Optional[List[Dict[str, Any]]] = []

class TestRunResult(BaseModel):
    run_id: str
    test_case: str
    url: str
    status: str
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    nodes: List[ElementNode] = []
    edges: List[Edge] = []
    logs: List[str] = []
