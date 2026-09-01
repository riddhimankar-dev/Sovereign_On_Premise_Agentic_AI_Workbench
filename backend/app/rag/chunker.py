from typing import List, Dict, Any
import tiktoken
from app.core.logging import get_logger

logger = get_logger(__name__)

try:
    ENCODER = tiktoken.get_encoding("cl100k_base")
except Exception:
    ENCODER = None


def count_tokens(text: str) -> int:
    if ENCODER:
        return len(ENCODER.encode(text))
    return len(text) // 4


def chunk_text(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    min_chunk_size: int = 50,
) -> List[str]:
    if not text or not text.strip():
        return []

    tokens = ENCODER.encode(text) if ENCODER else text.split()
    if not tokens:
        return []

    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        if ENCODER:
            chunk_text = ENCODER.decode(chunk_tokens)
        else:
            chunk_text = " ".join(chunk_tokens)

        if len(chunk_text.strip()) >= min_chunk_size:
            chunks.append(chunk_text.strip())

        if end >= len(tokens):
            break
        start = end - chunk_overlap

    return chunks


def chunk_pages(
    pages: List[Dict[str, Any]],
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    doc_metadata: Dict[str, Any] = None,
) -> List[Dict[str, Any]]:
    doc_metadata = doc_metadata or {}
    # Convert enums to strings for JSON serialization
    clean_metadata = {}
    for k, v in doc_metadata.items():
        if hasattr(v, 'value'):
            clean_metadata[k] = v.value
        else:
            clean_metadata[k] = v
    
    chunks = []

    for page in pages:
        page_num = page.get("page_number", 0)
        text = page.get("text", "")
        section = page.get("section", "")

        page_chunks = chunk_text(text, chunk_size, chunk_overlap)
        for i, chunk_text_content in enumerate(page_chunks):
            chunk = {
                "content": chunk_text_content,
                "page_number": page_num,
                "section": section,
                "chunk_index": len(chunks),
                "token_count": count_tokens(chunk_text_content),
                "metadata": {
                    **clean_metadata,
                    "page": page_num,
                    "section": section,
                },
            }
            chunks.append(chunk)

    return chunks