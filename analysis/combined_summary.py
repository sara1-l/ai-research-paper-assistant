"""
Generate a structured multi-paper summary from extracted data.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, List


def _normalize_for_counting(s: str) -> List[str]:
    """Extract meaningful terms from a string for frequency counting."""
    if not s or s == "N/A":
        return []
    s = s.lower()
    terms = []
    for t in s.replace(",", " ").replace(".", " ").split():
        t = t.strip()
        if len(t) > 4 and t not in ("that", "this", "with", "from", "have", "been", "were", "their"):
            terms.append(t)
    return terms


def _format_paper_summary(p: dict, idx: int) -> str:
    """Format a single paper's structured data as summary text."""
    return (
        f"**Paper {idx} Summary**\n\n"
        f"**Title:** {p.get('title', 'N/A')}\n"
        f"**Problem:** {p.get('research_problem', 'N/A')}\n"
        f"**Methodology:** {p.get('methodology', 'N/A')}\n"
        f"**Dataset:** {p.get('dataset_used', 'N/A')}\n"
        f"**Results:** {p.get('key_results', 'N/A')}\n"
        f"**Limitations:** {p.get('limitations', 'N/A')}\n"
    )


def generate_combined_summary(structured_papers: List[dict[str, Any]]) -> tuple[list[str], str]:
    """
    Generate a structured multi-paper summary from extracted data.

    Describes: common research problems, methodologies, datasets, major findings.

    Parameters
    ----------
    structured_papers : list of dict
        Structured paper data from paper_analyzer.

    Returns
    -------
    tuple of (list of str, str)
        (paper_summaries, overall_summary)
    """
    if not structured_papers:
        return ([], "No papers to summarize.")

    paper_summaries = [
        _format_paper_summary(p, i + 1)
        for i, p in enumerate(structured_papers)
    ]

    # Aggregate methodologies
    methods = []
    for p in structured_papers:
        m = p.get("methodology", "") or ""
        if m and m != "N/A":
            methods.append(m)
    method_terms = _normalize_for_counting(" ".join(methods))
    top_methods = Counter(method_terms).most_common(5)

    # Aggregate datasets
    datasets = [p.get("dataset_used", "") for p in structured_papers if p.get("dataset_used") and p.get("dataset_used") != "N/A"]
    dataset_str = ", ".join(set(datasets)) if datasets else "Various datasets"

    # Aggregate problems
    problems = [p.get("research_problem", "") for p in structured_papers if p.get("research_problem") and p.get("research_problem") != "N/A"]

    # Build synthesis text for AI
    synthesis = (
        f"Research papers analyzed: {len(structured_papers)}. "
        f"Common methodologies include: {', '.join(t[0] for t in top_methods) if top_methods else 'varied'}. "
        f"Datasets used: {dataset_str}. "
        f"Research problems: {'; '.join(problems[:3]) if problems else 'varied'}. "
    )
    for i, p in enumerate(structured_papers[:3], 1):
        r = p.get("key_results", "") or ""
        if r and r != "N/A":
            synthesis += f" Paper {i} results: {r[:150]}. "

    try:
        from ai_models.summarizer import summarize_text

        structured = summarize_text(synthesis[:2500])
        parts = [
            structured.get("problem", ""),
            structured.get("methodology", ""),
            structured.get("results", ""),
            structured.get("conclusion", ""),
        ]
        overall = " ".join(p for p in parts if p).strip() or synthesis
    except Exception:
        overall = (
            f"Most papers focus on related research problems using machine learning and statistical methods. "
            f"Common methodologies include: {', '.join(t[0] for t in top_methods[:3]) if top_methods else 'varied approaches'}. "
            f"Datasets used across studies: {dataset_str}. "
            f"Key findings vary by paper; review the comparison table for details."
        )
    return (paper_summaries, overall)
