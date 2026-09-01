from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.core.logging import get_logger

logger = get_logger(__name__)


class ToolInput(BaseModel):
    pass


class ToolOutput(BaseModel):
    success: bool
    data: Any = None
    error: Optional[str] = None


class BaseTool(ABC):
    name: str
    description: str
    permission: str = "read"

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> ToolOutput:
        pass

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "permission": self.permission,
        }


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        return {name: tool.get_schema() for name, tool in self._tools.items()}


tool_registry = ToolRegistry()