"""
Research gap analysis: identify missing research areas and underexplored topics.

Uses summarization and heuristics to analyze paper summaries and suggest gaps.
"""

from __future__ import annotations

import re
from typing import List

from ai_models.summarizer import summarize_text


def _extract_key_themes(summaries: List[str]) -> List[str]:
    """Extract recurring themes/keywords from summaries (simple heuristic)."""
    combined = " ".join(summaries).lower()
    # Common research terms
    terms = [
        "machine learning", "deep learning", "neural network", "dataset",
        "accuracy", "model", "algorithm", "evaluation", "benchmark",
        "supervised", "unsupervised", "reinforcement", "transformer",
        "groundwater", "contamination", "satellite", "remote sensing",
    ]
    found = []
    for t in terms:
        if t in combined and t not in found:
            found.append(t)
    return found[:10]


def _identify_limitations(summaries: List[str]) -> List[str]:
    """Look for limitation/ future work phrases."""
    limits = []
    limit_keywords = ["limitation", "future work", "further research", "not explored", "lacking"]
    for s in summaries:
        for kw in limit_keywords:
            if kw in s.lower():
                # Extract sentence containing keyword
                for sent in re.split(r"[.!?]", s):
                    if kw in sent.lower() and len(sent) > 30:
                        limits.append(sent.strip()[:200])
                        break
    return limits[:5]


def analyze_research_gaps(summaries: List[str]) -> str:
    """
    Analyze paper summaries and generate a research gap analysis.

    Parameters
    ----------
    summaries : list of str
        Combined or individual paper summaries (e.g. problem + methodology + results + conclusion).

    Returns
    -------
    str
        A textual analysis of research gaps, limitations, and opportunities.
    """
    if not summaries:
        return "No summaries available for gap analysis."

    # Build combined text for analysis
    combined = "\n\n".join(s[:1500] for s in summaries if s)
    if not combined.strip():
        return "No content available for gap analysis."

    themes = _extract_key_themes(summaries)
    limitations = _identify_limitations(summaries)

    # Use summarizer to synthesize combined content; captures high-level themes
    try:
        structured = summarize_text(combined[:2500])
        gap_summary = " ".join(
            str(v) for v in structured.values() if v and str(v).strip()
        ).strip()
        if gap_summary:
            gap_summary = (
                "Based on the analyzed papers: " + gap_summary + " "
                "Few studies may explore the intersection of these themes in depth, "
                "indicating potential research opportunities for interdisciplinary work."
            )
    except Exception:
        gap_summary = ""

    # Build output
    parts = []

    if gap_summary:
        parts.append(gap_summary)

    if themes:
        parts.append("\n\n**Recurring themes across papers:** " + ", ".join(themes))

    if limitations:
        parts.append("\n\n**Identified limitations:**")
        for i, lim in enumerate(limitations, 1):
            parts.append(f"  {i}. {lim}")

    if not parts:
        return (
            "Few studies explore the intersection of themes found across the papers. "
            "This indicates a potential research opportunity for interdisciplinary work."
        )

    return "\n".join(parts).strip()
