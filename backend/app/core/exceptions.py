from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class WorkbenchException(Exception):
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


class ModelUnavailableError(WorkbenchException):
    def __init__(self, model: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Model '{model}' is unavailable",
            code="MODEL_UNAVAILABLE",
            details=details or {"model": model},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class OllamaConnectionError(WorkbenchException):
    def __init__(self, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            "Cannot connect to Ollama service",
            code="OLLAMA_CONNECTION_ERROR",
            details=details,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class QdrantConnectionError(WorkbenchException):
    def __init__(self, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            "Cannot connect to Qdrant vector database",
            code="QDRANT_CONNECTION_ERROR",
            details=details,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class IngestionError(WorkbenchException):
    def __init__(self, message: str, document_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            code="INGESTION_ERROR",
            details=details or {"document_id": document_id},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class DocumentNotFoundError(WorkbenchException):
    def __init__(self, document_id: str):
        super().__init__(
            f"Document '{document_id}' not found",
            code="DOCUMENT_NOT_FOUND",
            details={"document_id": document_id},
            status_code=status.HTTP_404_NOT_FOUND,
        )


class RetrievalError(WorkbenchException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            code="RETRIEVAL_ERROR",
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class AgentExecutionError(WorkbenchException):
    def __init__(self, message: str, run_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            code="AGENT_EXECUTION_ERROR",
            details=details or {"run_id": run_id},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class ToolExecutionError(WorkbenchException):
    def __init__(self, tool_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Tool '{tool_name}' failed: {message}",
            code="TOOL_EXECUTION_ERROR",
            details=details or {"tool": tool_name},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class SandboxError(WorkbenchException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            code="SANDBOX_ERROR",
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class DocumentGenerationError(WorkbenchException):
    def __init__(self, message: str, artifact_type: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            code="DOCUMENT_GENERATION_ERROR",
            details=details or {"artifact_type": artifact_type},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class UnauthorizedError(WorkbenchException):
    def __init__(self, message: str = "Unauthorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            code="UNAUTHORIZED",
            details=details,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenError(WorkbenchException):
    def __init__(self, message: str = "Forbidden", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            code="FORBIDDEN",
            details=details,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ValidationError(WorkbenchException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            code="VALIDATION_ERROR",
            details=details,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class OfflineModeError(WorkbenchException):
    def __init__(self, message: str = "Operation requires external network but offline mode is enabled"):
        super().__init__(
            message,
            code="OFFLINE_MODE_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
        )