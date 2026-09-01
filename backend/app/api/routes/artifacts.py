from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.db.models import Artifact, ArtifactStatus, ArtifactType, DocumentClassification, Project
from app.core.config import settings
import os

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


class ArtifactResponse(BaseModel):
    id: int
    artifact_id: str
    project_id: Optional[int]
    name: str
    artifact_type: str
    file_path: Optional[str]
    status: str
    classification: str
    created_by: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ArtifactListResponse(BaseModel):
    artifacts: List[ArtifactResponse]
    total: int


@router.get("", response_model=ArtifactListResponse)
async def list_artifacts(
    project_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Artifact).join(Project, Artifact.project_id == Project.id, isouter=True).filter(
        (Project.company_id == settings.company_id) | (Artifact.company_id == settings.company_id)
    )
    if project_id:
        query = query.filter(Artifact.project_id == project_id)
    if status:
        query = query.filter(Artifact.status == status)
    total = query.count()
    artifacts = query.order_by(Artifact.created_at.desc()).offset(offset).limit(limit).all()
    return ArtifactListResponse(
        artifacts=[ArtifactResponse.model_validate(a) for a in artifacts],
        total=total,
    )


@router.get("/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(artifact_id: str, db: Session = Depends(get_db)):
    artifact = db.query(Artifact).filter(Artifact.artifact_id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return ArtifactResponse.model_validate(artifact)


@router.get("/{artifact_id}/download")
async def download_artifact(artifact_id: str, db: Session = Depends(get_db)):
    artifact = db.query(Artifact).filter(Artifact.artifact_id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    if not artifact.file_path or not os.path.exists(artifact.file_path):
        raise HTTPException(status_code=404, detail="Artifact file not found")

    with open(artifact.file_path, "rb") as f:
        content = f.read()

    media_type = "application/octet-stream"
    if artifact.artifact_type == ArtifactType.DOCX:
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif artifact.artifact_type == ArtifactType.XLSX:
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif artifact.artifact_type == ArtifactType.PPTX:
        media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    elif artifact.artifact_type == ArtifactType.PDF:
        media_type = "application/pdf"
    elif artifact.artifact_type == ArtifactType.PY:
        media_type = "text/x-python"
    elif artifact.artifact_type == ArtifactType.JSON:
        media_type = "application/json"

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{artifact.name}.{artifact.artifact_type.value.lower()}"'}
    )