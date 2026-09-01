from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.db.database import get_db
from app.db.models import Document, DocumentStatus, DocumentType, DocumentClassification, Company
from app.core.config import settings
from app.core.logging import get_logger
import os
import uuid
from datetime import datetime

logger = get_logger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


def _iso_or_none(value) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return value.isoformat()


class DocumentResponse(BaseModel):
    id: int
    document_id: str
    file_name: str
    file_path: str
    file_type: str
    file_size: int
    page_count: Optional[int] = None
    classification: str
    status: str
    owner: Optional[str]
    revision: Optional[str]
    uploaded_at: Optional[str] = None
    indexed_at: Optional[str] = None
    error_message: Optional[str]

    @classmethod
    def from_orm_compat(cls, doc) -> "DocumentResponse":
        return cls(
            id=doc.id,
            document_id=doc.document_id,
            file_name=doc.file_name,
            file_path=doc.file_path,
            file_type=(doc.file_type.value if hasattr(doc.file_type, "value") else doc.file_type),
            file_size=doc.file_size,
            page_count=doc.page_count,
            classification=(doc.classification.value if hasattr(doc.classification, "value") else doc.classification),
            status=(doc.status.value if hasattr(doc.status, "value") else doc.status),
            owner=doc.owner,
            revision=doc.revision,
            uploaded_at=_iso_or_none(doc.uploaded_at),
            indexed_at=_iso_or_none(doc.indexed_at),
            error_message=doc.error_message,
        )

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int


class UploadResponse(BaseModel):
    document_id: str
    file_name: str
    status: str


UPLOAD_DIR = "/home/aum/Desktop/ML/Smart India Hackathon/backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    company_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Document)
    if company_id:
        query = query.filter(Document.company_id == company_id)
    else:
        query = query.filter(Document.company_id == settings.company_id)
    if status:
        query = query.filter(Document.status == status)
    total = query.count()
    documents = query.order_by(Document.uploaded_at.desc()).offset(offset).limit(limit).all()
    return DocumentListResponse(
        documents=[DocumentResponse.from_orm_compat(doc) for doc in documents],
        total=total,
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    classification: str = Form("INTERNAL"),
    asset_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    file_ext = os.path.splitext(file.filename)[1].lower()
    file_type_map = {
        ".pdf": DocumentType.PDF,
        ".docx": DocumentType.DOCX,
        ".xlsx": DocumentType.XLSX,
        ".pptx": DocumentType.PPTX,
        ".txt": DocumentType.TXT,
        ".jpg": DocumentType.IMAGE,
        ".jpeg": DocumentType.IMAGE,
        ".png": DocumentType.IMAGE,
        ".tiff": DocumentType.IMAGE,
        ".tif": DocumentType.IMAGE,
    }
    file_type = file_type_map.get(file_ext, DocumentType.OTHER)

    document_id = str(uuid.uuid4())
    safe_filename = f"{document_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    file_size = len(content)

    try:
        class_val = DocumentClassification[classification.upper()]
    except KeyError:
        class_val = DocumentClassification.INTERNAL

    document = Document(
        document_id=document_id,
        company_id=settings.company_id,
        file_name=file.filename,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        page_count=0,
        classification=class_val,
        status=DocumentStatus.UPLOADING,
        owner="system",
        uploaded_by=1,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        document.status = DocumentStatus.PROCESSING
        db.commit()

        from app.rag.parser import parse_document
        from app.rag.chunker import chunk_document
        from app.rag.embeddings import get_embeddings
        from app.rag.vector_store import vector_store

        text_content = await parse_document(file_path, file_type.value)
        chunks = chunk_document(text_content, document_id=document_id)
        document.page_count = len(chunks)

        if chunks:
            embeddings = await get_embeddings([c["content"] for c in chunks])
            from app.db.models import DocumentChunk
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                doc_chunk = DocumentChunk(
                    document_id=document.id,
                    chunk_index=i,
                    content=chunk["content"],
                    page_number=chunk.get("page_number"),
                    section=chunk.get("section"),
                    token_count=chunk.get("token_count"),
                    embedding=embedding,
                    chunk_metadata=chunk.get("metadata", {}),
                )
                db.add(doc_chunk)
            db.commit()

            await vector_store.upsert_chunks(
                company_id=settings.company_id,
                document_id=document_id,
                chunks=[{
                    "id": f"{document_id}_{i}",
                    "content": c["content"],
                    "embedding": e,
                    "metadata": {
                        "document_id": document_id,
                        "chunk_index": i,
                        "page_number": c.get("page_number"),
                        "section": c.get("section"),
                    }
                } for i, (c, e) in enumerate(zip(chunks, embeddings))]
            )

        document.status = DocumentStatus.READY
        document.indexed_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        logger.error("document_processing_failed", document_id=document_id, error=str(e))
        document.status = DocumentStatus.ERROR
        document.error_message = str(e)
        db.commit()

    return UploadResponse(document_id=document_id, file_name=file.filename, status=document.status.value)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse.from_orm_compat(document)


@router.delete("/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    db.delete(document)
    db.commit()
    return {"success": True}