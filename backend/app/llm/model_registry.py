from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.models import ModelRegistry, ModelStatus
from app.db.repositories import ModelRegistryRepository
from app.llm.ollama_client import ollama_client
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

MODEL_DEFINITIONS = [
    {
        "model_id": "qwen2.5:7b",
        "role": "reasoning",
        "provider": "ollama",
        "is_local": True,
        "capabilities": ["reasoning", "summarization", "technical_analysis", "structured_output", "document_analysis"],
        "context_length": 32768,
        "vram_usage_gb": 4.7,
    },
    {
        "model_id": "qwen2.5-coder:7b",
        "role": "coding",
        "provider": "ollama",
        "is_local": True,
        "capabilities": ["code_generation", "code_explanation", "debugging", "code_review", "test_generation"],
        "context_length": 32768,
        "vram_usage_gb": 4.7,
    },
    {
        "model_id": "qwen2.5:3b",
        "role": "router",
        "provider": "ollama",
        "is_local": True,
        "capabilities": ["classification", "routing", "intent_detection", "lightweight_extraction"],
        "context_length": 32768,
        "vram_usage_gb": 1.9,
    },
    {
        "model_id": "bge-m3:latest",
        "role": "embedding",
        "provider": "ollama",
        "is_local": True,
        "capabilities": ["embeddings", "semantic_search", "retrieval"],
        "context_length": 8192,
        "vram_usage_gb": 1.2,
    },
]


class ModelRegistryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ModelRegistryRepository(db)

    def initialize(self) -> List[ModelRegistry]:
        models = []
        for defn in MODEL_DEFINITIONS:
            model = self.repo.upsert(**defn, status=ModelStatus.UNAVAILABLE)
            models.append(model)
        return models

    async def check_availability(self) -> Dict[str, bool]:
        results = {}
        for defn in MODEL_DEFINITIONS:
            model_id = defn["model_id"]
            try:
                available = await ollama_client.is_model_available(model_id)
                status = ModelStatus.READY if available else ModelStatus.UNAVAILABLE
                self.repo.upsert(model_id=model_id, status=status)
                results[model_id] = available
            except Exception as e:
                logger.error("model_check_failed", model=model_id, error=str(e))
                self.repo.upsert(model_id=model_id, status=ModelStatus.ERROR)
                results[model_id] = False
        return results

    def get_models(self) -> List[ModelRegistry]:
        return self.repo.list()

    def get_by_role(self, role: str) -> Optional[ModelRegistry]:
        models = self.repo.list()
        for m in models:
            if m.role == role:
                return m
        return None

    def get_model_for_task(self, task_type: str) -> str:
        if task_type in ("code", "coding", "calculation", "python"):
            return settings.coding_model
        elif task_type in ("classification", "routing", "intent"):
            return settings.router_model
        elif task_type == "embedding":
            return settings.embedding_model
        else:
            return settings.primary_model

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        model = self.repo.get_by_id(model_id)
        if not model:
            return None
        return {
            "id": model.model_id,
            "role": model.role,
            "provider": model.provider,
            "local": model.is_local,
            "status": model.status.value,
            "capabilities": model.capabilities,
            "context_length": model.context_length,
            "vram_usage_gb": model.vram_usage_gb,
        }

    def list_models_for_ui(self) -> List[Dict[str, Any]]:
        models = self.repo.list()
        result = []
        for m in models:
            result.append({
                "id": m.model_id,
                "tag": m.role.upper(),
                "name": m.model_id.replace(":", " ").title(),
                "role": m.role,
                "provider": m.provider,
                "local": m.is_local,
                "status": m.status.value,
                "capabilities": m.capabilities,
                "context_length": m.context_length,
                "vram_usage_gb": m.vram_usage_gb,
            })
        return result