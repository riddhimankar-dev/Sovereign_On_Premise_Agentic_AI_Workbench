from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.db.database import get_db
from app.rag.retriever import HybridRetriever
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    asset_id: Optional[str] = None
    document_type: Optional[str] = None
    classification: Optional[str] = None


class SearchResult(BaseModel):
    chunk_id: int
    document_id: str
    content: str
    page_number: int
    section: Optional[str]
    score: float
    metadata: dict


class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    total: int


@router.post("/search", response_model=SearchResponse)
async def search_knowledge(
    request: SearchRequest,
    db: Session = Depends(get_db),
):
    company_id = settings.company_id
    retriever = HybridRetriever(db)

    results = await retriever.retrieve_with_metadata(
        query=request.query,
        company_id=company_id,
        asset_id=request.asset_id,
        document_type=request.document_type,
        classification=request.classification,
        limit=request.limit,
    )

    return SearchResponse(
        results=[SearchResult(**r) for r in results],
        query=request.query,
        total=len(results),
    )


@router.get("/health")
async def knowledge_health():
    return {"status": "ok", "service": "knowledge"}