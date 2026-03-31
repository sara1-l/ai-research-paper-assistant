from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from sqlalchemy import delete, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from database.models import RagChunk
from database.session import get_engine, init_db


@dataclass
class PgVectorStore:
    engine: Engine
    document_id: str

    def upsert_document(self, chunks: List[str], embeddings: np.ndarray) -> None:
        if embeddings.ndim != 2:
            raise ValueError("embeddings must be 2D (n_chunks, dim).")
        if len(chunks) != embeddings.shape[0]:
            raise ValueError("chunks and embeddings length mismatch.")

        init_db(self.engine)

        with Session(self.engine) as session:
            session.execute(delete(RagChunk).where(RagChunk.document_id == self.document_id))
            session.add_all(
                [
                    RagChunk(
                        document_id=self.document_id,
                        chunk_index=i,
                        chunk_text=chunk,
                        embedding=embeddings[i].astype("float32").tolist(),
                    )
                    for i, chunk in enumerate(chunks)
                ]
            )
            session.commit()

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        if query_embedding.ndim == 2:
            query_embedding = query_embedding[0]
        q = query_embedding.astype("float32").tolist()

        with Session(self.engine) as session:
            stmt = (
                select(
                    RagChunk.chunk_text,
                    RagChunk.embedding.l2_distance(q).label("distance"),
                )
                .where(RagChunk.document_id == self.document_id)
                .order_by("distance")
                .limit(int(top_k))
            )
            rows = session.execute(stmt).all()

        return [(row[0], float(row[1])) for row in rows]


__all__ = ["PgVectorStore", "get_engine"]
