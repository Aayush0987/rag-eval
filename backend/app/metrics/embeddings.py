from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer


@lru_cache
def _model() -> SentenceTransformer:
    return SentenceTransformer("all-MiniLM-L6-v2")


def cosine_similarity(text_a: str, text_b: str) -> float:
    embeddings = _model().encode([text_a, text_b], normalize_embeddings=True)
    return float(np.dot(embeddings[0], embeddings[1]))
