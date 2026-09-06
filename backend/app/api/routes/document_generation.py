from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
from app.db.database import get_db
from app.db.models import Artifact, ArtifactType, ArtifactStatus, DocumentClassification, Project
from app.services.file_document_generator import (
    render_document,
    SUPPORTED_TEMPLATES,
    SECTION_TEMPLATES,
)
from app.core.config import settings
import os
import uuid

router = APIRouter(prefix="/documents/generate", tags=["document-generation"])

ARTIFACT_DIR = "/home/aum/Desktop/ML/Smart India Hackathon/backend/artifacts"
os.makedirs(ARTIFACT_DIR, exist_ok=True)


class GenerateRequest(BaseModel):
    template: str
    data: Dict[str, Any]
    format: str
    project_id: Optional[int] = None
    name: Optional[str] = None


class GenerateResponse(BaseModel):
    artifact_id: str
    file_path: str
    download_url: str


@router.post("", response_model=GenerateResponse)
async def generate_document(request: GenerateRequest, db: Session = Depends(get_db)):
    project = None
    if request.project_id:
        project = db.query(Project).filter(Project.id == request.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

    ext = request.format.lower()
    if request.template not in SUPPORTED_TEMPLATES or ext not in SUPPORTED_TEMPLATES[request.template]:
        raise HTTPException(status_code=400, detail=f"Unsupported template/format: {request.template}/{ext}")

    artifact_id = str(uuid.uuid4())
    file_name = f"{artifact_id}.{ext}"
    file_path = os.path.join(ARTIFACT_DIR, file_name)

    try:
        content = render_document(request.template, ext, request.data)

        with open(file_path, "wb") as f:
            f.write(content)

        artifact = Artifact(
            artifact_id=artifact_id,
            company_id=settings.company_id,
            project_id=request.project_id,
            name=request.name or f"{request.template}_{datetime.utcnow().strftime('%Y%m%d')}",
            artifact_type=ArtifactType(ext.upper()),
            file_path=file_path,
            status=ArtifactStatus.READY_FOR_REVIEW,
            classification=DocumentClassification.CONFIDENTIAL,
            created_by=1,
            sources=[],
        )
        db.add(artifact)
        db.commit()

        return GenerateResponse(
            artifact_id=artifact_id,
            file_path=file_path,
            download_url=f"/api/artifacts/{artifact_id}/download",
        )

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Document generation failed: {str(e)}")
