from typing import List, Dict, Any
from app.db.repositories import DocumentChunkRepository
from app.core.logging import get_logger

logger = get_logger(__name__)

try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False
    BM25Okapi = None


class KeywordSearch:
    def __init__(self, db):
        self.db = db
        self.chunk_repo = DocumentChunkRepository(db)
        self._corpus = []
        self._chunk_ids = []
        self._bm25 = None
        self._initialized = False

    def _initialize(self, company_id: str):
        if self._initialized or not BM25_AVAILABLE:
            return

        from app.db.repositories import DocumentRepository
        doc_repo = DocumentRepository(self.db)
        docs = doc_repo.list(company_id)
        doc_ids = [d.id for d in docs]

        for doc_id in doc_ids:
            doc_chunks = self.chunk_repo.get_by_document(doc_id)
            for chunk in doc_chunks:
                self._corpus.append(chunk.content.lower().split())
                self._chunk_ids.append(chunk.id)

        if self._corpus and BM25Okapi:
            self._bm25 = BM25Okapi(self._corpus)
        self._initialized = True

    def search(self, query: str, company_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        self._initialize(company_id)

        if not self._bm25 or not self._corpus or not BM25_AVAILABLE:
            return []

        tokenized_query = query.lower().split()
        scores = self._bm25.get_scores(tokenized_query)

        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:limit]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append({
                    "chunk_id": self._chunk_ids[idx],
                    "score": float(scores[idx]),
                })

        return results


def create_keyword_search(db) -> KeywordSearch:
    return KeywordSearch(db)