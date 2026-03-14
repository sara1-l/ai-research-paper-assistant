from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

import faiss
import numpy as np


@dataclass
class VectorStore:
    """
    Lightweight wrapper around a FAISS index and associated metadata.

    Attributes
    ----------
    index : faiss.Index
        The underlying FAISS index used for similarity search.
    embeddings : np.ndarray
        Original embedding matrix of shape (n_items, dim).
    metadata : List[str]
        Metadata associated with each embedding; in this project we
        typically store the corresponding text chunk here.
    """

    index: faiss.Index
    embeddings: np.ndarray
    metadata: List[str]

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Search the index for the most similar chunks to the query embedding.

        Parameters
        ----------
        query_embedding : np.ndarray
            Vector representation of the query, shape (dim,) or (1, dim).
        top_k : int, optional
            Number of most similar results to return.

        Returns
        -------
        List[Tuple[str, float]]
            A list of (chunk_text, distance) tuples, sorted by increasing
            distance (i.e. most similar first when using L2).
        """
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        distances, indices = self.index.search(query_embedding.astype("float32"), top_k)
        distances = distances[0]
        indices = indices[0]

        results: List[Tuple[str, float]] = []
        for idx, dist in zip(indices, distances):
            if idx < 0 or idx >= len(self.metadata):
                continue
            results.append((self.metadata[idx], float(dist)))
        return results


def create_faiss_index(embeddings: np.ndarray, chunks: Sequence[str]) -> VectorStore:
    """
    Create a FAISS index from the given embeddings and bind it with text chunks.

    Parameters
    ----------
    embeddings : np.ndarray
        2D array of shape (n_items, dim) containing embedding vectors.
    chunks : Sequence[str]
        Text chunks corresponding to each embedding vector.

    Returns
    -------
    VectorStore
        A VectorStore instance with a populated FAISS index.

    Raises
    ------
    ValueError
        If the shapes of embeddings and chunks do not align or
        embeddings are not 2D.
    """
    if embeddings.ndim != 2:
        raise ValueError("embeddings must be a 2D array of shape (n_items, dim).")

    n_items, dim = embeddings.shape
    if n_items != len(chunks):
        raise ValueError(
            f"Number of embeddings ({n_items}) does not match number of chunks ({len(chunks)})."
        )

    # FAISS expects float32
    emb_float32 = embeddings.astype("float32")

    # Simple L2 index; can be swapped for other index types later.
    index = faiss.IndexFlatL2(dim)
    index.add(emb_float32)

    return VectorStore(index=index, embeddings=emb_float32, metadata=list(chunks))


def search_similar_chunks(
    vector_store: VectorStore,
    query_embedding: np.ndarray,
    top_k: int = 5,
) -> List[Tuple[str, float]]:
    """
    Convenience wrapper that delegates to VectorStore.search.

    Parameters
    ----------
    vector_store : VectorStore
        The vector store instance to search in.
    query_embedding : np.ndarray
        Embedding vector for the query.
    top_k : int, optional
        Number of results to return.

    Returns
    -------
    List[Tuple[str, float]]
        List of (chunk_text, distance) tuples.
    """
    return vector_store.search(query_embedding, top_k=top_k)

