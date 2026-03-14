"""
Build a comparison table from structured paper data.
"""

from __future__ import annotations

from typing import Any, List

import pandas as pd


def build_comparison_table(structured_papers: List[dict[str, Any]]) -> pd.DataFrame:
    """
    Build a pandas DataFrame comparing all papers.

    Parameters
    ----------
    structured_papers : list of dict
        Each dict has keys: title, research_problem, methodology,
        dataset_used, key_results, limitations.

    Returns
    -------
    pandas.DataFrame
        Columns: Paper, Research Problem, Methodology, Dataset,
        Results, Limitations.
    """
    rows = []
    for p in structured_papers:
        rows.append({
            "Paper": p.get("title", "N/A"),
            "Research Problem": p.get("research_problem", "N/A"),
            "Methodology": p.get("methodology", "N/A"),
            "Dataset": p.get("dataset_used", "N/A"),
            "Results": p.get("key_results", "N/A"),
            "Limitations": p.get("limitations", "N/A"),
        })
    return pd.DataFrame(rows)
