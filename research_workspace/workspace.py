"""
Research Workspace: orchestration for multi-paper analysis.

Handles combined summary, comparison table, trend graphs, research gap,
and current paper context analysis.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import pandas as pd

from ai_models.summarizer import summarize_text
from pdf_processing.extract_text import extract_text_from_pdf
from research_workspace.paper_comparator import build_comparison_table
from research_workspace.research_gap import analyze_research_gaps
from visualization.trend_graphs import generate_trend_graphs


def extract_texts_from_paths(paths: List[str]) -> List[Tuple[str, str]]:
    """
    Extract text from multiple PDF paths. Returns (path, text) tuples.
    Skips files that fail extraction.
    """
    results = []
    for p in paths:
        try:
            text = extract_text_from_pdf(str(p))
            results.append((str(p), text or ""))
        except Exception:
            results.append((str(p), ""))
    return results


def generate_combined_summary(
    papers: List[Tuple[str, str]],
    current_paper_title: str | None = None,
) -> Tuple[List[str], str]:
    """
    Generate per-paper summaries and an overall combined summary.

    Parameters
    ----------
    papers : list of (path, text)
    current_paper_title : str, optional
        Title for the first paper.

    Returns
    -------
    (paper_summaries, overall_summary)
        paper_summaries: list of "Paper N Summary: ..." strings
        overall_summary: combined "Overall Research Summary" string
    """
    paper_summaries = []
    all_summary_texts = []

    for i, (path, text) in enumerate(papers):
        if not text or not text.strip():
            title = Path(path).stem
            paper_summaries.append(f"**Paper {i + 1} Summary** ({title}): No text extracted.")
            continue
        try:
            structured = summarize_text(text[:3000])
            parts = [
                f"**Problem:** {structured.get('problem', 'N/A')}",
                f"**Methodology:** {structured.get('methodology', 'N/A')}",
                f"**Results:** {structured.get('results', 'N/A')}",
                f"**Conclusion:** {structured.get('conclusion', 'N/A')}",
            ]
            summary = "\n".join(parts)
            paper_summaries.append(f"**Paper {i + 1} Summary**\n\n{summary}")
            all_summary_texts.append(summary)
        except Exception:
            paper_summaries.append(f"**Paper {i + 1} Summary** ({Path(path).stem}): Summarization failed.")
            all_summary_texts.append("")

    # Overall summary from concatenated summaries
    combined_for_overall = "\n\n".join(s for s in all_summary_texts if s)
    overall_summary = ""
    if combined_for_overall.strip():
        try:
            structured = summarize_text(combined_for_overall[:3000])
            overall_summary = (
                f"**Problem:** {structured.get('problem', 'N/A')}\n"
                f"**Methodology:** {structured.get('methodology', 'N/A')}\n"
                f"**Results:** {structured.get('results', 'N/A')}\n"
                f"**Conclusion:** {structured.get('conclusion', 'N/A')}"
            )
        except Exception:
            overall_summary = "Could not generate overall summary."
    else:
        overall_summary = "No summaries available for overall synthesis."

    return paper_summaries, overall_summary


def get_comparison_table(
    papers: List[Tuple[str, str]],
    current_paper_title: str | None = None,
) -> pd.DataFrame:
    """Build comparison table from papers."""
    return build_comparison_table(papers, current_paper_title=current_paper_title)


def get_trend_graphs(comparison_df: pd.DataFrame) -> dict:
    """Generate trend graphs from comparison table."""
    return generate_trend_graphs(comparison_df)


def get_research_gap_analysis(summaries: List[str]) -> str:
    """Analyze research gaps from paper summaries."""
    return analyze_research_gaps(summaries)


def analyze_current_paper_context(
    current_text: str,
    other_summaries: List[str],
) -> str:
    """
    Compare current paper against past papers.
    Output: how it differs, new contributions, whether it fills research gaps.
    """
    if not current_text or not current_text.strip():
        return "No text available for current paper analysis."

    try:
        current_summary = summarize_text(current_text[:2000])
    except Exception:
        current_summary = {"problem": "N/A", "methodology": "N/A", "results": "N/A", "conclusion": "N/A"}

    combined_others = "\n\n".join(s for s in other_summaries[:3] if s)
    if not combined_others.strip():
        return (
            "**Current Paper Summary:**\n"
            f"- Problem: {current_summary.get('problem', 'N/A')}\n"
            f"- Methodology: {current_summary.get('methodology', 'N/A')}\n"
            f"- Results: {current_summary.get('results', 'N/A')}\n"
            f"- Conclusion: {current_summary.get('conclusion', 'N/A')}\n\n"
            "Upload at least one supporting paper to enable comparison."
        )

    parts = [
        "**Current Paper Summary:**",
        f"- Problem: {current_summary.get('problem', 'N/A')}",
        f"- Methodology: {current_summary.get('methodology', 'N/A')}",
        f"- Results: {current_summary.get('results', 'N/A')}",
        f"- Conclusion: {current_summary.get('conclusion', 'N/A')}",
        "",
        "**How the current paper differs:**",
        "Compare the problem and methodology above with supporting papers. "
        "Differences emerge from scope, methods, and target applications.",
        "",
        "**What new contributions it makes:**",
        "Review Results and Conclusion against other papers for novel findings or improved metrics.",
        "",
        "**Whether it fills any research gap:**",
        "Cross-reference the Research Gap Analysis tab with this paper's problem and conclusion.",
    ]
    return "\n".join(parts)
