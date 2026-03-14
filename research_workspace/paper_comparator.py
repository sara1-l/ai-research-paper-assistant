"""
Paper comparator: extract metadata and build comparison table using NLP heuristics.

Extracts Title, Authors, Year, Methodology, Dataset Used, Results from paper text.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd

from pdf_processing.extract_text import extract_text_from_pdf


@dataclass
class PaperInfo:
    """Extracted metadata for a single paper."""

    title: str
    authors: str
    year: str
    methodology: str
    dataset_used: str
    results: str


def _extract_year(text: str) -> str:
    """Extract publication year using regex (19xx or 20xx)."""
    matches = re.findall(r"\b(19[5-9]\d|20[0-3]\d)\b", text[:5000])
    return str(matches[0]) if matches else "N/A"


def _extract_authors(text: str) -> str:
    """Heuristic: look for author-like patterns in first 2000 chars."""
    head = text[:2000]
    # Common patterns: "Authors: X, Y, Z" or "by X and Y" or "X, Y, Z (Year)"
    m = re.search(r"(?:authors?|by)\s*[:\-]?\s*([^.]+?)(?:\d{4}|$|\n\n)", head, re.I)
    if m:
        raw = m.group(1).strip()
        # Clean and take first few names
        names = [n.strip() for n in re.split(r",|\band\b", raw) if len(n.strip()) > 2][:5]
        return ", ".join(names) if names else "N/A"
    return "N/A"


def _extract_section(text: str, keywords: List[str], max_chars: int = 400) -> str:
    """Extract a section by finding sentences containing keywords."""
    text_lower = text.lower()
    sentences = re.split(r"[.!?]\s+", text)
    for kw in keywords:
        for s in sentences:
            if kw in s.lower() and len(s) > 20:
                cleaned = s.strip()[:max_chars]
                return cleaned + ("..." if len(s) > max_chars else "")
    return "N/A"


def _extract_methodology(text: str) -> str:
    """Extract methodology/approach description."""
    keywords = [
        "methodology", "approach", "we propose", "algorithm", "model",
        "framework", "method", "technique", "we use", "we employ"
    ]
    return _extract_section(text, keywords, 350)


def _extract_dataset(text: str) -> str:
    """Extract dataset/benchmark information."""
    keywords = [
        "dataset", "benchmark", "evaluation on", "we use", "trained on",
        "evaluated on", "datasets", "corpus", "ImageNet", "MNIST", "COCO"
    ]
    return _extract_section(text, keywords, 300)


def _extract_results(text: str) -> str:
    """Extract results/performance description."""
    keywords = [
        "accuracy", "results", "achieved", "performance", "achieves",
        "outperforms", "improvement", "F1", "precision", "recall", "%"
    ]
    return _extract_section(text, keywords, 350)


def _extract_title(file_path: str, text: str) -> str:
    """Use filename as fallback title, or first non-empty line."""
    name = Path(file_path).stem
    name = name.replace("_", " ").replace("-", " ").strip()
    if name:
        return name[:200]
    first_line = text.strip().split("\n")[0][:200] if text.strip() else "Unknown"
    return first_line or "N/A"


def extract_paper_info(file_path: str, text: str, title_override: str | None = None) -> PaperInfo:
    """
    Extract structured metadata from paper text using NLP heuristics.

    Parameters
    ----------
    file_path : str
        Path to the PDF file (used for title fallback).
    text : str
        Extracted full text from the PDF.
    title_override : str, optional
        If provided, use this as the title.

    Returns
    -------
    PaperInfo
        Extracted metadata.
    """
    title = title_override or _extract_title(file_path, text)
    return PaperInfo(
        title=title[:200] if title else "N/A",
        authors=_extract_authors(text),
        year=_extract_year(text),
        methodology=_extract_methodology(text),
        dataset_used=_extract_dataset(text),
        results=_extract_results(text),
    )


def build_comparison_table(
    papers: List[tuple[str, str]],
    current_paper_title: str | None = None,
) -> pd.DataFrame:
    """
    Build a comparison DataFrame from multiple (file_path, text) pairs.

    Parameters
    ----------
    papers : list of (file_path, text)
        Each tuple is (path, extracted_text).
    current_paper_title : str, optional
        Title for the first/current paper if known.

    Returns
    -------
    pandas.DataFrame
        Columns: Title, Authors, Year, Methodology, Dataset Used, Results.
    """
    rows = []
    for i, (path, text) in enumerate(papers):
        if not text or not text.strip():
            rows.append({
                "Title": Path(path).stem,
                "Authors": "N/A",
                "Year": "N/A",
                "Methodology": "N/A",
                "Dataset Used": "N/A",
                "Results": "N/A",
            })
            continue
        override = current_paper_title if i == 0 and current_paper_title else None
        info = extract_paper_info(path, text, title_override=override)
        rows.append({
            "Title": info.title,
            "Authors": info.authors,
            "Year": info.year,
            "Methodology": info.methodology,
            "Dataset Used": info.dataset_used,
            "Results": info.results,
        })
    return pd.DataFrame(rows)
