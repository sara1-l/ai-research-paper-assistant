from __future__ import annotations

from typing import Iterable, List

import numpy as np
from sentence_transformers import SentenceTransformer

_EMBEDDING_MODEL: SentenceTransformer | None = None


def _get_embedding_model() -> SentenceTransformer:
    """
    Lazily load and cache the SentenceTransformer model.

    Uses the 'all-MiniLM-L6-v2' model as requested.
    """
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        _EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _EMBEDDING_MODEL


def generate_embeddings(text_chunks: Iterable[str]) -> np.ndarray:
    """
    Generate dense vector embeddings for a collection of text chunks.

    Parameters
    ----------
    text_chunks : Iterable[str]
        An iterable of text segments (e.g. sentences or document chunks).

    Returns
    -------
    numpy.ndarray
        A 2D array of shape (n_chunks, embedding_dim) containing
        the embedding vectors. If no valid chunks are provided, an
        empty array with shape (0, embedding_dim) is returned.

    Raises
    ------
    ValueError
        If all provided chunks are empty or whitespace-only.
    RuntimeError
        If embedding generation fails for any reason.
    """
    model = _get_embedding_model()

    # Normalize and filter out empty chunks to avoid unnecessary computation.
    cleaned_chunks: List[str] = [
        chunk.strip()
        for chunk in text_chunks
        if isinstance(chunk, str) and chunk.strip()
    ]

    if not cleaned_chunks:
        raise ValueError("No non-empty text chunks provided for embedding generation.")

    try:
        embeddings = model.encode(cleaned_chunks, convert_to_numpy=True, show_progress_bar=False)
    except Exception as exc:
        raise RuntimeError("Failed to generate embeddings with SentenceTransformers.") from exc

    # Ensure result is a 2D numpy array for consistent downstream use.
    embeddings = np.asarray(embeddings)
    if embeddings.ndim == 1:
        embeddings = embeddings.reshape(1, -1)

    return embeddings

