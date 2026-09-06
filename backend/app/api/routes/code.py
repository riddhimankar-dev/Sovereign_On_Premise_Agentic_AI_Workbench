from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import uuid
from app.db.database import get_db
from app.api.dependencies import get_current_user
from app.db.models import AuditEvent, User
from app.tools.code_executor import CodeExecutorTool
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/code", tags=["code-sandbox"])

executor = CodeExecutorTool()


class CodeRunRequest(BaseModel):
    code: str
    language: str = "python"
    timeout: int = 30


class CodeRunResponse(BaseModel):
    stdout: str
    stderr: str
    return_code: int
    execution_ms: int
    sandbox: str


@router.post("/run", response_model=CodeRunResponse)
async def run_code(
    payload: CodeRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payload.code.strip():
        raise HTTPException(status_code=400, detail="No code provided")
    if payload.timeout < 1 or payload.timeout > 60:
        raise HTTPException(status_code=400, detail="timeout must be between 1 and 60 seconds")

    import time
    start = time.time()
    result = await executor.execute(
        {"code": payload.code, "timeout": payload.timeout, "language": payload.language},
        {"db": db, "user_id": current_user.id},
    )
    elapsed = int((time.time() - start) * 1000)

    try:
        db.add(AuditEvent(
            event_id=str(uuid.uuid4()),
            company_id=current_user.company_id,
            user_id=current_user.id,
            event_type="code.run",
            resource_type="sandbox",
            resource_id=f"code-{uuid.uuid4().hex[:10]}",
            details={"language": payload.language, "success": result.success, "return_code": result.data.get("return_code") if result.data else None},
        ))
        db.commit()
    except Exception as e:
        logger.error("code_audit_failed", error=str(e))
        db.rollback()

    if not result.success:
        raise HTTPException(status_code=422, detail=result.error or "Sandbox execution failed")

    return CodeRunResponse(
        stdout=result.data.get("stdout", ""),
        stderr=result.data.get("stderr", ""),
        return_code=result.data.get("return_code", 0),
        execution_ms=elapsed,
        sandbox="isolated temp dir · python -I · no network · CPU/fs limits",
    )