from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.db.models import Approval, ApprovalStatus, Artifact, Project
from app.core.config import settings

router = APIRouter(prefix="/approvals", tags=["approvals"])


class ApprovalResponse(BaseModel):
    id: int
    approval_id: str
    artifact_id: int
    requested_by: int
    reviewed_by: Optional[int]
    status: str
    comments: Optional[str]
    requested_at: str
    reviewed_at: Optional[str]

    class Config:
        from_attributes = True


class ApprovalListResponse(BaseModel):
    approvals: List[ApprovalResponse]
    total: int


class ApprovalAction(BaseModel):
    comments: Optional[str] = None


@router.get("", response_model=ApprovalListResponse)
async def list_approvals(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Approval).join(Artifact).join(Project, Artifact.project_id == Project.id, isouter=True).filter(
        (Project.company_id == settings.company_id) | (Artifact.company_id == settings.company_id)
    )
    if status:
        query = query.filter(Approval.status == status)
    total = query.count()
    approvals = query.order_by(Approval.requested_at.desc()).offset(offset).limit(limit).all()
    return ApprovalListResponse(
        approvals=[ApprovalResponse.model_validate(a) for a in approvals],
        total=total,
    )


@router.get("/{approval_id}", response_model=ApprovalResponse)
async def get_approval(approval_id: str, db: Session = Depends(get_db)):
    approval = db.query(Approval).filter(Approval.approval_id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    return ApprovalResponse.model_validate(approval)


@router.post("/{approval_id}/approve", response_model=ApprovalResponse)
async def approve_approval(approval_id: str, action: ApprovalAction, db: Session = Depends(get_db)):
    approval = db.query(Approval).filter(Approval.approval_id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")

    approval.status = ApprovalStatus.APPROVED
    approval.reviewed_by = 1
    approval.reviewed_at = datetime.utcnow()
    approval.comments = action.comments
    db.commit()
    db.refresh(approval)
    return ApprovalResponse.model_validate(approval)


@router.post("/{approval_id}/reject", response_model=ApprovalResponse)
async def reject_approval(approval_id: str, action: ApprovalAction, db: Session = Depends(get_db)):
    approval = db.query(Approval).filter(Approval.approval_id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")

    approval.status = ApprovalStatus.REJECTED
    approval.reviewed_by = 1
    approval.reviewed_at = datetime.utcnow()
    approval.comments = action.comments
    db.commit()
    db.refresh(approval)
    return ApprovalResponse.model_validate(approval)