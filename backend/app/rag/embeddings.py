from typing import List
from app.llm.ollama_client import ollama_client
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def get_embedding(text: str, model: str = None) -> List[float]:
    model = model or settings.embedding_model
    try:
        embedding = await ollama_client.embeddings(model, text)
        return embedding
    except Exception as e:
        logger.error("embedding_failed", model=model, error=str(e))
        raise


async def get_embeddings_batch(texts: List[str], model: str = None) -> List[List[float]]:
    embeddings = []
    for text in texts:
        emb = await get_embedding(text, model)
        embeddings.append(emb)
    return embeddings