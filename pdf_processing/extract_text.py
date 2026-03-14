import os
from typing import Optional

import fitz  # PyMuPDF


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract full text content from a PDF file using PyMuPDF.

    Parameters
    ----------
    file_path : str
        Path to the PDF file on disk.

    Returns
    -------
    str
        Concatenated text from all pages of the PDF.

    Raises
    ------
    FileNotFoundError
        If the provided path does not point to an existing file.
    RuntimeError
        If the PDF cannot be opened or read for any reason.
    """
    if not isinstance(file_path, str) or not file_path.strip():
        raise ValueError("file_path must be a non-empty string.")

    normalized_path = os.path.abspath(file_path)

    if not os.path.isfile(normalized_path):
        # Explicit check helps distinguish missing file from parsing issues.
        raise FileNotFoundError(f"PDF file not found: {normalized_path}")

    try:
        document = fitz.open(normalized_path)
    except Exception as exc:  # PyMuPDF can throw various low-level errors
        raise RuntimeError(f"Failed to open PDF: {normalized_path}") from exc

    text_chunks = []
    try:
        for page_index in range(len(document)):
            try:
                page = document.load_page(page_index)
                page_text: Optional[str] = page.get_text("text")
                if page_text:
                    text_chunks.append(page_text)
            except Exception as page_exc:
                # Skip problematic pages but continue with the rest of the document.
                # This keeps the function robust against partially corrupted PDFs.
                # If strict behavior is desired later, this branch can re-raise instead.
                continue
    finally:
        document.close()

    if not text_chunks:
        # Provide a clear signal to callers that no text was recovered.
        # Callers can decide whether to treat this as an error.
        return ""

    # Joining with double newlines preserves loose page boundaries without
    # introducing additional formatting assumptions.
    return "\n\n".join(text_chunks)

