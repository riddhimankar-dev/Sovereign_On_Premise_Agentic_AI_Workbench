from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.llm.model_registry import ModelRegistryService
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/models", tags=["models"])


@router.get("")
async def list_models(db: Session = Depends(get_db)):
    service = ModelRegistryService(db)
    models = service.list_models_for_ui()
    return {"models": models}


@router.get("/{model_id}")
async def get_model(model_id: str, db: Session = Depends(get_db)):
    service = ModelRegistryService(db)
    info = service.get_model_info(model_id)
    if not info:
        return {"error": "Model not found"}
    return info


@router.post("/check-availability")
async def check_availability(db: Session = Depends(get_db)):
    service = ModelRegistryService(db)
    results = await service.check_availability()
    return {"availability": results}


@router.post("/initialize")
async def initialize_models(db: Session = Depends(get_db)):
    service = ModelRegistryService(db)
    models = service.initialize()
    return {"initialized": len(models), "models": [m.model_id for m in models]}