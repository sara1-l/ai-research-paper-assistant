"""
Research gap detection derived from paper limitations.

Algorithm:
1. Collect limitations from all papers
2. Identify repeated limitations
3. Identify missing methodologies or datasets
4. Generate a research gap statement
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, List


def _extract_limitation_themes(limitations: List[str]) -> List[str]:
    """Extract recurring themes from limitation text."""
    combined = " ".join(limitations).lower()
    themes = []
    # Common limitation phrases
    patterns = [
        (r"limited\s+(?:to|by|in)\s+([^.,]+)", "limited scope"),
        (r"small\s+(?:dataset|sample)", "small dataset"),
        (r"single\s+(?:region|area|domain)", "single region/domain"),
        (r"lack\s+of\s+([^.,]+)", "lack of data/resources"),
        (r"not\s+explore[ds]?\s+([^.,]+)", "underexplored area"),
        (r"future\s+work", "future work needed"),
        (r"deep\s+learning", "deep learning"),
        (r"machine\s+learning", "traditional ML"),
        (r"satellite\s+data", "satellite data"),
        (r"real-?time", "real-time"),
        (r"large-?scale", "large-scale"),
    ]
    for pat, label in patterns:
        if re.search(pat, combined):
            themes.append(label)
    return list(dict.fromkeys(themes))


def _get_methodologies_used(structured_papers: List[dict]) -> set:
    """Get set of methodology terms mentioned across papers."""
    used = set()
    ml_terms = ["machine learning", "deep learning", "random forest", "svm", "neural", "lstm", "transformer"]
    for p in structured_papers:
        m = (p.get("methodology", "") or "").lower()
        for t in ml_terms:
            if t in m:
                used.add(t)
    return used


def _get_datasets_used(structured_papers: List[dict]) -> set:
    """Get set of dataset types mentioned."""
    used = set()
    for p in structured_papers:
        d = (p.get("dataset_used", "") or "").lower()
        if "satellite" in d or "remote" in d:
            used.add("satellite")
        if "imagenet" in d or "mnist" in d or "benchmark" in d:
            used.add("standard benchmark")
        if "custom" in d or "proprietary" in d:
            used.add("custom")
    return used


def get_gap_themes(structured_papers: List[dict[str, Any]]) -> List[str]:
    """Extract limitation themes for use in current paper analysis."""
    limitations = [
        p.get("limitations", "") or ""
        for p in structured_papers
        if p.get("limitations") and p.get("limitations") != "N/A"
    ]
    if not limitations:
        return []
    return _extract_limitation_themes(limitations)


def detect_research_gaps(structured_papers: List[dict[str, Any]]) -> str:
    """
    Derive research gap statement from paper limitations.

    Parameters
    ----------
    structured_papers : list of dict
        Structured paper data from paper_analyzer.

    Returns
    -------
    str
        Research gap analysis text.
    """
    if not structured_papers:
        return "No papers available for gap analysis."

    limitations = [
        p.get("limitations", "") or ""
        for p in structured_papers
        if p.get("limitations") and p.get("limitations") != "N/A"
    ]
    if not limitations:
        limitations = [
            p.get("research_problem", "") or ""
            for p in structured_papers
        ]

    themes = _extract_limitation_themes(limitations)
    methods_used = _get_methodologies_used(structured_papers)
    datasets_used = _get_datasets_used(structured_papers)

    parts = []

    # Repeated limitations
    if themes:
        parts.append(
            f"**Analysis of uploaded papers:** "
            f"Recurring limitations include: {', '.join(themes[:5])}."
        )

    # Missing methodologies
    if "deep learning" not in methods_used and "neural" not in methods_used:
        parts.append(
            "Most studies rely on traditional machine learning models (e.g., Random Forest, SVM). "
            "Very few explore deep learning techniques."
        )
    if "transformer" not in methods_used and "lstm" not in methods_used:
        parts.append(
            "Advanced architectures such as Transformers or LSTMs are largely absent."
        )

    # Missing datasets
    if "satellite" not in datasets_used:
        parts.append(
            "Limited use of satellite or remote sensing datasets."
        )

    # Build gap statement
    parts.append(
        "\n\n**Research Gap:** "
        "There is limited research combining the methodologies and datasets "
        "that are underutilized across the reviewed papers. Future work could "
        "address the repeated limitations (e.g., small datasets, single domains) "
        "by exploring alternative methods and larger-scale datasets."
    )

    return " ".join(parts).strip()
