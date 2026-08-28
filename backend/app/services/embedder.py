import numpy as np
import logging
from typing import List
from app.config import settings

logger = logging.getLogger("hybrid_rag.embedder")

class DenseEmbeddingService:
    def __init__(self, dimension: int = settings.EMBEDDING_DIMENSION):
        self.dimension = dimension

    def embed_text(self, text: str) -> List[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                embeddings = []
                for text in texts:
                    res = client.models.embed_content(model=settings.EMBEDDING_MODEL, contents=text)
                    vec = res.embedding.values if hasattr(res, 'embedding') else self._fallback_embedding(text)
                    arr = np.array(vec, dtype=np.float32)
                    norm = np.linalg.norm(arr)
                    if norm > 0: arr = arr / norm
                    embeddings.append(arr.tolist())
                return embeddings
            except Exception as e:
                logger.warning(f"Gemini embed failed: {e}")
        return [self._fallback_embedding(t) for t in texts]

    def _fallback_embedding(self, text: str) -> List[float]:
        vec = np.zeros(self.dimension, dtype=np.float32)
        words = text.lower().split()
        for i, w in enumerate(words):
            h = hash(w) % self.dimension
            vec[h] += 1.0 / (1.0 + i * 0.01)
        norm = np.linalg.norm(vec)
        if norm > 0: vec = vec / norm
        else: vec[0] = 1.0
        return vec.tolist()

embedder_service = DenseEmbeddingService()
