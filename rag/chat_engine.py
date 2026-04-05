from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol, Tuple

import numpy as np

from pdf_processing.extract_text import extract_text_from_pdf
from rag.vector_store import create_faiss_index
from database.session import get_engine
from rag.pgvector_store import PgVectorStore
from utils.text_splitter import simple_text_splitter
from utils.doc_ids import stable_document_id
import os


class SearchableStore(Protocol):
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]: ...


@dataclass
class RAGSession:
    """
    Encapsulates the state required for a Retrieval-Augmented Generation flow.

    A typical lifetime is:
    - create from an uploaded PDF path
    - answer multiple questions using the built index
    """

    chunks: List[str]
    embeddings: np.ndarray
    vector_store: SearchableStore

    @classmethod
    def from_pdf(
        cls,
        pdf_path: str,
        max_chars: int = 1000,
        overlap: int = 100,
    ) -> "RAGSession":
        """
        Build a RAGSession from a PDF file path.

        Steps:
        1. Extract text from the PDF.
        2. Split the text into overlapping chunks.
        3. Generate embeddings for those chunks.
        4. Store embeddings and chunks in a FAISS-based VectorStore.
        """
        from ai_models.embeddings import generate_embeddings

        full_text = extract_text_from_pdf(pdf_path)
        chunks = simple_text_splitter(full_text, max_chars=max_chars, overlap=overlap)
        embeddings = generate_embeddings(chunks)
        backend = os.getenv("VECTOR_BACKEND", "faiss").strip().lower()
        if backend == "pgvector":
            doc_id = stable_document_id(pdf_path)
            store = PgVectorStore(engine=get_engine(), document_id=doc_id)
            store.upsert_document(chunks=chunks, embeddings=embeddings)
            vector_store = store
        else:
            vector_store = create_faiss_index(embeddings, chunks)
        return cls(chunks=chunks, embeddings=embeddings, vector_store=vector_store)

    def answer_question(self, question: str, top_k: int = 5) -> str:
        """
        Answer a user question based on the indexed PDF content.

        This baseline implementation:
        - embeds the user question
        - retrieves the most similar chunks
        - concatenates them as a context answer

        In a full system, this context would be passed to a generative
        model (e.g. an LLM) to produce a natural-language answer.
        """
        if not question or not question.strip():
            raise ValueError("Question must be a non-empty string.")

        from ai_models.embeddings import generate_embeddings

        # Generate a single embedding for the question.
        question_embedding = generate_embeddings([question])[0]

        # Retrieve the most relevant chunks.
        retrieved = self.vector_store.search(question_embedding, top_k=top_k)
        retrieved_chunks = [chunk for chunk, _ in retrieved]

        if not retrieved_chunks:
            return "I could not find relevant information in the document to answer that question."

        # Simple baseline: just return the concatenated relevant chunks.
        # This keeps the chat engine independent of any specific LLM.
        return "\n\n".join(retrieved_chunks)


def process_uploaded_pdf(pdf_path: str) -> RAGSession:
    """
    Convenience function for the application layer.

    Given the path to an uploaded PDF, prepare a RAGSession that
    can be reused to answer multiple questions about that document.
    """
    return RAGSession.from_pdf(pdf_path)


def answer_question_from_session(session: RAGSession, question: str, top_k: int = 5) -> str:
    """
    Small wrapper to keep the application code simple and declarative.
    """
    return session.answer_question(question, top_k=top_k)

