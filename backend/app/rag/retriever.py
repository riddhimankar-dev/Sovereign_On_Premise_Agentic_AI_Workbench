from typing import List, Dict, Any, Optional
from app.rag.embeddings import get_embedding
from app.rag.vector_store import vector_store
from app.rag.keyword_search import create_keyword_search
from app.db.repositories import DocumentChunkRepository
from app.db.models import DocumentChunk, Document
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class HybridRetriever:
    def __init__(self, db):
        self.db = db
        self.chunk_repo = DocumentChunkRepository(db)
        self.keyword_search = create_keyword_search(db)

    async def retrieve(
        self,
        query: str,
        company_id: str,
        limit: int = 10,
        metadata_filter: Dict[str, Any] = None,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ) -> List[Dict[str, Any]]:
        query_embedding = await get_embedding(query)

        semantic_results = vector_store.search(
            vector=query_embedding,
            company_id=company_id,
            limit=limit * 2,
            metadata_filter=metadata_filter,
        )

        keyword_results = self.keyword_search.search(query, company_id, limit * 2)

        combined = self._merge_results(
            semantic_results,
            keyword_results,
            semantic_weight,
            keyword_weight,
            limit,
        )

        return combined

    def _merge_results(
        self,
        semantic: List[Dict[str, Any]],
        keyword: List[Dict[str, Any]],
        sem_weight: float,
        kw_weight: float,
        limit: int,
    ) -> List[Dict[str, Any]]:
        score_map = {}

        for r in semantic:
            chunk_id = r["payload"].get("chunk_id") or r["id"]
            score_map[chunk_id] = score_map.get(chunk_id, 0) + r["score"] * sem_weight

        for r in keyword:
            score_map[r["chunk_id"]] = score_map.get(r["chunk_id"], 0) + r["score"] * kw_weight

        sorted_chunks = sorted(score_map.items(), key=lambda x: x[1], reverse=True)[:limit]

        results = []
        for chunk_id, score in sorted_chunks:
            chunk_obj = self.db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
            if chunk_obj:
                doc = self.db.query(Document).filter(Document.id == chunk_obj.document_id).first()
                doc_id_str = doc.document_id if doc else str(chunk_obj.document_id)
                results.append({
                    "chunk_id": chunk_id,
                    "document_id": doc_id_str,
                    "content": chunk_obj.content,
                    "page_number": chunk_obj.page_number,
                    "section": chunk_obj.section,
                    "score": score,
                    "metadata": chunk_obj.chunk_metadata,
                })

        return results

    async def retrieve_with_metadata(
        self,
        query: str,
        company_id: str,
        asset_id: str = None,
        document_type: str = None,
        classification: str = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        metadata_filter = {}
        if asset_id:
            metadata_filter["asset_id"] = asset_id
        if document_type:
            metadata_filter["document_type"] = document_type
        if classification:
            metadata_filter["classification"] = classification

        return await self.retrieve(query, company_id, limit, metadata_filter)