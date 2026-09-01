from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.db.database import get_db
from app.core.config import settings
from app.core.logging import get_logger
import httpx

logger = get_logger(__name__)
router = APIRouter(prefix="/security", tags=["security"])


class SecurityItem(BaseModel):
    label: str
    status: str
    status_color: str
    status_bg: str
    desc: str
    indicator: str


class SecurityStatusResponse(BaseModel):
    items: List[SecurityItem]
    overall: str


@router.get("/status", response_model=SecurityStatusResponse)
async def security_status(db: Session = Depends(get_db)):
    checks = {}

    try:
        db.execute("SELECT 1")
        checks["database"] = True
    except Exception as e:
        logger.error("database_check_failed", error=str(e))
        checks["database"] = False

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            checks["ollama"] = resp.status_code == 200
    except Exception as e:
        logger.error("ollama_check_failed", error=str(e))
        checks["ollama"] = False

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.qdrant_url}/health")
            checks["qdrant"] = resp.status_code == 200
    except Exception as e:
        logger.error("qdrant_check_failed", error=str(e))
        checks["qdrant"] = False

    items = [
        SecurityItem(
            label="Internet Access",
            status="BLOCKED",
            status_color="text-[#EF4444]",
            status_bg="bg-[#EF4444]/10 border-[#EF4444]/20",
            desc="No outbound internet connections are permitted from the AI environment.",
            indicator="blocked",
        ),
        SecurityItem(
            label="External AI APIs",
            status="BLOCKED",
            status_color="text-[#EF4444]",
            status_bg="bg-[#EF4444]/10 border-[#EF4444]/20",
            desc="Connections to OpenAI, Anthropic, Google, and other external model providers are disabled.",
            indicator="blocked",
        ),
        SecurityItem(
            label="Cloud AI Services",
            status="DISABLED",
            status_color="text-[#667386]",
            status_bg="bg-[#253248] border-[#253248]",
            desc="Cloud-hosted AI workloads are not in use. All inference runs on local hardware.",
            indicator="disabled",
        ),
        SecurityItem(
            label="Local Model Inference",
            status="ACTIVE" if checks.get("ollama") else "UNAVAILABLE",
            status_color="text-[#14B8A6]" if checks.get("ollama") else "text-[#EF4444]",
            status_bg="bg-[#14B8A6]/10 border-[#14B8A6]/20" if checks.get("ollama") else "bg-[#EF4444]/10 border-[#EF4444]/20",
            desc="Local models run on NVIDIA RTX A5000 hardware within the organization's infrastructure.",
            indicator="active" if checks.get("ollama") else "blocked",
        ),
        SecurityItem(
            label="Local Storage",
            status="ACTIVE" if checks.get("database") else "UNAVAILABLE",
            status_color="text-[#14B8A6]" if checks.get("database") else "text-[#EF4444]",
            status_bg="bg-[#14B8A6]/10 border-[#14B8A6]/20" if checks.get("database") else "bg-[#EF4444]/10 border-[#EF4444]/20",
            desc="All documents, artifacts, and knowledge are stored on organization-controlled storage.",
            indicator="active" if checks.get("database") else "blocked",
        ),
        SecurityItem(
            label="Sandbox Network",
            status="BLOCKED",
            status_color="text-[#EF4444]",
            status_bg="bg-[#EF4444]/10 border-[#EF4444]/20",
            desc="Code execution containers have no network access. Filesystem is isolated per run.",
            indicator="blocked",
        ),
        SecurityItem(
            label="Audit Logging",
            status="ACTIVE" if checks.get("database") else "UNAVAILABLE",
            status_color="text-[#14B8A6]" if checks.get("database") else "text-[#EF4444]",
            status_bg="bg-[#14B8A6]/10 border-[#14B8A6]/20" if checks.get("database") else "bg-[#EF4444]/10 border-[#EF4444]/20",
            desc="All AI interactions, file accesses, and approvals are logged for compliance and traceability.",
            indicator="active" if checks.get("database") else "blocked",
        ),
    ]

    all_secure = all(checks.values())
    overall = "secure" if all_secure else "degraded"

    return SecurityStatusResponse(items=items, overall=overall)