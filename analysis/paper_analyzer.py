"""
Structured paper extraction using AI and heuristics.

Extracts: Title, Research Problem, Methodology, Dataset Used,
Key Results, Limitations for each paper.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List


def _extract_title(file_path: str, text: str) -> str:
    """Extract title from filename or first meaningful line."""
    name = Path(file_path).stem.replace("_", " ").replace("-", " ").strip()
    if len(name) > 10:
        return name[:200]
    first_lines = [l.strip() for l in text[:500].split("\n") if len(l.strip()) > 20]
    return first_lines[0][:200] if first_lines else name or "Unknown"


def _extract_dataset_heuristic(text: str) -> str:
    """Extract dataset/benchmark mentions using keywords."""
    text_lower = text.lower()
    # Well-known datasets (case-insensitive match, return canonical name)
    known = [
        ("imagenet", "ImageNet"), ("mnist", "MNIST"), ("coco", "COCO"),
        ("squad", "SQuAD"), ("glue", "GLUE"), ("uci", "UCI"), ("kaggle", "Kaggle"),
        ("satellite", "Satellite data"), ("groundwater", "Groundwater dataset"),
        ("remote sensing", "Remote sensing data"),
    ]
    for kw, canonical in known:
        if kw in text_lower:
            return canonical
    # Generic patterns
    patterns = [
        r"(?:dataset|benchmark|evaluated on|trained on|we use)\s*[:\-]?\s*([^.]+?)(?:\.|;|\n)",
        r"(?:using|with)\s+(?:the\s+)?([A-Za-z0-9\s\-]+?\s+(?:dataset|benchmark|corpus))",
    ]
    for pat in patterns:
        matches = re.findall(pat, text_lower, re.I)
        for m in matches:
            cleaned = (m.strip() if isinstance(m, str) else m[0].strip())[:100]
            if 5 < len(cleaned) < 150:
                return cleaned
    return "N/A"


def _extract_limitations_heuristic(text: str, max_sentences: int = 2) -> str:
    """Extract limitation sentences from text."""
    keywords = [
        "limitation", "limited", "however", "future work", "further research",
        "drawback", "constraint", "not explore", "lack of", "small dataset",
        "single region", "one drawback", "main limitation",
    ]
    sentences = re.split(r"[.!?]\s+", text)
    found = []
    for s in sentences:
        s_lower = s.lower()
        if any(kw in s_lower for kw in keywords) and len(s.strip()) > 30:
            found.append(s.strip()[:300])
            if len(found) >= max_sentences:
                break
    return ". ".join(found) if found else "N/A"


def analyze_paper(file_path: str, text: str, title_override: str | None = None) -> Dict[str, Any]:
    """
    Extract structured research information from a single paper.

    Parameters
    ----------
    file_path : str
        Path to the PDF file.
    text : str
        Extracted full text from the PDF.
    title_override : str, optional
        Override the extracted title.

    Returns
    -------
    dict
        Keys: title, research_problem, methodology, dataset_used,
        key_results, limitations.
    """
    if not text or not text.strip():
        return {
            "title": title_override or _extract_title(file_path, ""),
            "research_problem": "N/A",
            "methodology": "N/A",
            "dataset_used": "N/A",
            "key_results": "N/A",
            "limitations": "N/A",
        }

    title = title_override or _extract_title(file_path, text)
    dataset = _extract_dataset_heuristic(text[:4000])
    limitations = _extract_limitations_heuristic(text[:4000])

    try:
        from ai_models.summarizer import summarize_text

        structured = summarize_text(text[:3000])
        problem = structured.get("problem", "N/A")
        methodology = structured.get("methodology", "N/A")
        results = structured.get("results", "N/A")
        conclusion = structured.get("conclusion", "N/A")
    except Exception:
        problem = methodology = results = conclusion = "N/A"

    if limitations == "N/A" and conclusion:
        limitations = conclusion[:400]

    return {
        "title": title[:200],
        "research_problem": (problem or "N/A")[:500],
        "methodology": (methodology or "N/A")[:400],
        "dataset_used": dataset if dataset else "N/A",
        "key_results": (results or "N/A")[:400],
        "limitations": (limitations or "N/A")[:400],
    }


def analyze_papers(
    papers: List[tuple[str, str]],
    current_paper_title: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Extract structured info from multiple papers.

    Parameters
    ----------
    papers : list of (file_path, text)
    current_paper_title : str, optional
        Title for the first (current) paper.

    Returns
    -------
    list of dict
        One structured dict per paper.
    """
    results = []
    for i, (path, text) in enumerate(papers):
        override = current_paper_title if i == 0 else None
        results.append(analyze_paper(path, text or "", title_override=override))
    return results
