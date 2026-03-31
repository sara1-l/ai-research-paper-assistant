from __future__ import annotations

import hashlib
from pathlib import Path


def stable_document_id(pdf_path: str) -> str:
    """
    Produce a stable-ish document id for a local PDF path.

    We avoid hashing full file content to keep this fast for large PDFs.
    """
    p = Path(pdf_path)
    try:
        stat = p.stat()
        payload = f"{p.name}|{stat.st_size}|{int(stat.st_mtime)}"
    except OSError:
        payload = p.name
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()

