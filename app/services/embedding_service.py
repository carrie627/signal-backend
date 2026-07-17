from functools import lru_cache

import numpy as np
# from sentence_transformers import SentenceTransformer
from fastembed import TextEmbedding

from app.core.config import get_settings
from app.data.service_catalog import SERVICE_CATALOG


def _normalize(vec: np.ndarray):
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec

# @lru_cache
# def _get_model() -> SentenceTransformer:
#     # Loaded once per process and reused — this is the expensive part
#     # (model weights into RAM), so it must not happen per-request.
#     settings = get_settings()
#     return SentenceTransformer(settings.embedding_model_name)

@lru_cache
def _get_model() -> TextEmbedding:
    # Loaded once per process and reused — this is the expensive part
    # (model weights into RAM), so it must not happen per-request.
    settings = get_settings()
    print(settings.embedding_model_name)
    return TextEmbedding(model_name=settings.embedding_model_name)


# @lru_cache
# def _get_catalog_embeddings() -> np.ndarray:
#     # Catalog rarely changes, so these vectors are computed once at first
#     # use and kept in memory for the lifetime of the process.
#     model = _get_model()
#     texts = [f"{entry['name']}: {entry['description']}" for entry in SERVICE_CATALOG]
#     embeddings = model.encode(texts, normalize_embeddings=True)
#     return np.asarray(embeddings)

@lru_cache
def _get_catalog_embeddings() -> np.ndarray:
    model = _get_model()
    texts = [f"{entry['name']}: {entry['description']}" for entry in SERVICE_CATALOG]
    raw_vectors = list(model.embed(texts))
    return np.array([_normalize(np.asarray(v)) for v in raw_vectors])


def preload() -> None:
    """Call at app startup so the first real request isn't the one paying
    for model load + catalog embedding time."""
    _get_catalog_embeddings()


# def embed_text(text: str) -> np.ndarray:
#     model = _get_model()
#     return np.asarray(model.encode(text, normalize_embeddings=True))

def embed_text(text: str) -> np.ndarray:
    model = _get_model()
    raw_vector = next(iter(model.embed([text])))
    return _normalize(np.asarray(raw_vector))


def match_service(lead_embedding: np.ndarray) -> tuple[str, int]:
    """Returns (matched_service_name, confidence_0_to_100)."""
    catalog_embeddings = _get_catalog_embeddings()

    # Vectors are already normalized, so dot product == cosine similarity.
    similarities = catalog_embeddings @ lead_embedding
    best_index = int(np.argmax(similarities))
    best_score = float(similarities[best_index])

    confidence = max(0, min(100, round(best_score * 100)))
    return SERVICE_CATALOG[best_index]["name"], confidence
