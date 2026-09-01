from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import uuid
from app.core.logging import get_logger

logger = get_logger(__name__)


class AgentPhase(str, Enum):
    ROUTING = "routing"
    PLANNING = "planning"
    TOOL_EXECUTION = "tool_execution"
    RETRIEVAL = "retrieval"
    REASONING = "reasoning"
    VERIFICATION = "verification"
    ARTIFACT_GENERATION = "artifact_generation"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStepModel(BaseModel):
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    label: str
    tool: Optional[str] = None
    status: str = "pending"
    input_data: Dict[str, Any] = {}
    output_data: Dict[str, Any] = {}
    duration_ms: int = 0
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class AgentPlan(BaseModel):
    steps: List[AgentStepModel] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentState(BaseModel):
    run_id: str
    conversation_id: str
    user_id: int
    company_id: str
    query: str
    phase: AgentPhase = AgentPhase.ROUTING
    plan: Optional[AgentPlan] = None
    current_step_index: int = 0
    model_used: Optional[str] = None
    tools_used: List[str] = []
    documents_accessed: List[str] = []
    artifacts_generated: List[str] = []
    evidence: List[Dict[str, Any]] = []
    final_answer: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def get_current_step(self) -> Optional[AgentStepModel]:
        if self.plan and self.current_step_index < len(self.plan.steps):
            return self.plan.steps[self.current_step_index]
        return None

    def advance_step(self) -> bool:
        if self.plan and self.current_step_index < len(self.plan.steps):
            self.current_step_index += 1
            self.updated_at = datetime.utcnow()
            return True
        return False