"""
Compare the current (main) paper with past papers.

Output: how it differs, new methodology, whether it addresses research gaps.
"""

from __future__ import annotations

from typing import Any, List


def _methodology_diff(current: str, others: List[str]) -> str:
    """Describe methodology differences."""
    current_l = (current or "").lower()
    others_combined = " ".join(o or "" for o in others).lower()

    novel = []
    if "deep" in current_l and "deep" not in others_combined:
        novel.append("introduces deep learning")
    if "transformer" in current_l or "lstm" in current_l:
        if "transformer" not in others_combined and "lstm" not in others_combined:
            novel.append("uses advanced architectures (Transformer/LSTM)")
    if "satellite" in current_l or "remote" in current_l:
        if "satellite" not in others_combined and "remote" not in others_combined:
            novel.append("employs satellite/remote sensing data")

    if novel:
        return "The current paper " + ", ".join(novel) + "."
    return "The current paper uses a methodology that overlaps with some past studies."


def _gap_addressed(current: dict, gap_themes: List[str]) -> str:
    """Check if current paper addresses common gaps."""
    curr_lim = (current.get("limitations", "") or "").lower()
    curr_method = (current.get("methodology", "") or "").lower()
    curr_data = (current.get("dataset_used", "") or "").lower()

    addressed = []
    if "small dataset" in gap_themes and ("large" in curr_data or "benchmark" in curr_data):
        addressed.append("uses larger or benchmark datasets")
    if "deep learning" in gap_themes and "deep" in curr_method:
        addressed.append("introduces deep learning")
    if "satellite" in str(gap_themes).lower() and ("satellite" in curr_data or "remote" in curr_data):
        addressed.append("uses satellite/remote data")

    if addressed:
        return "The current paper addresses identified gaps by: " + "; ".join(addressed) + "."
    return "The current paper may partially address gaps; compare its methodology and dataset with the Research Gap analysis."


def analyze_current_paper_contribution(
    current_paper: dict[str, Any],
    other_papers: List[dict[str, Any]],
    gap_themes: List[str] | None = None,
) -> str:
    """
    Compare the main paper with past papers.

    Parameters
    ----------
    current_paper : dict
        Structured data for the current paper.
    other_papers : list of dict
        Structured data for supporting papers.
    gap_themes : list, optional
        Themes from research gap analysis.

    Returns
    -------
    str
        Analysis text with: how it differs, new methodology, gap addressing.
    """
    if not current_paper:
        return "No current paper data available."

    gap_themes = gap_themes or []
    other_methods = [p.get("methodology", "") for p in other_papers]
    other_problems = [p.get("research_problem", "") for p in other_papers]

    parts = []

    # How it differs
    curr_prob = current_paper.get("research_problem", "") or "N/A"
    parts.append("**How the current paper differs from past studies:**")
    if other_problems:
        parts.append(
            f"The current paper focuses on: {curr_prob[:300]}. "
            "Past studies address related but distinct problems; compare with the Comparison Table."
        )
    else:
        parts.append(f"The current paper addresses: {curr_prob[:300]}.")

    # New methodology
    parts.append("\n**What new methodology it introduces:**")
    method_diff = _methodology_diff(
        current_paper.get("methodology", ""),
        other_methods,
    )
    parts.append(method_diff)

    # Addresses gaps
    parts.append("\n**Whether it addresses any research gaps:**")
    parts.append(_gap_addressed(current_paper, gap_themes))

    return "\n".join(parts)
