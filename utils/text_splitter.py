from __future__ import annotations

from typing import List


def simple_text_splitter(text: str, max_chars: int = 1000, overlap: int = 100) -> List[str]:
    """
    Naive text splitter that chunks long strings into overlapping segments.

    This is intentionally simple and does not rely on any external libraries.
    It operates at the character level, which is sufficient as a baseline
    for feeding into embedding models.

    Parameters
    ----------
    text : str
        The input text to split.
    max_chars : int, optional
        Maximum number of characters per chunk.
    overlap : int, optional
        Number of overlapping characters between consecutive chunks to help
        preserve context across boundaries.

    Returns
    -------
    List[str]
        List of text chunks.
    """
    if not text:
        return []

    if max_chars <= 0:
        raise ValueError("max_chars must be a positive integer.")

    if overlap < 0:
        raise ValueError("overlap must be non-negative.")

    chunks: List[str] = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + max_chars, text_length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == text_length:
            break
        start = max(0, end - overlap)

    return chunks

