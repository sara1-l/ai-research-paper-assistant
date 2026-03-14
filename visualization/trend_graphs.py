"""
Trend graphs for research workspace: papers by year, methodology frequency, dataset usage.
"""

from __future__ import annotations

from typing import List

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go


def _safe_year(val) -> int | None:
    """Convert value to year int if valid."""
    if pd.isna(val) or val is None or val == "N/A":
        return None
    try:
        y = int(float(val))
        if 1900 <= y <= 2030:
            return y
    except (ValueError, TypeError):
        pass
    return None


def papers_by_year_chart(comparison_df: pd.DataFrame):
    """
    Create a bar chart of paper count by publication year.

    Parameters
    ----------
    comparison_df : pandas.DataFrame
        Must have a 'Year' column.
    """
    years = [
        _safe_year(v) for v in comparison_df["Year"].tolist()
        if _safe_year(v) is not None
    ]
    if not years:
        return None
    counts = pd.Series(years).value_counts().sort_index()
    fig = px.bar(
        x=counts.index.astype(str),
        y=counts.values,
        labels={"x": "Year", "y": "Number of Papers"},
        title="Papers by Publication Year",
    )
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Count",
        showlegend=False,
        margin=dict(t=50, b=50),
    )
    return fig


def methodology_frequency_chart(comparison_df: pd.DataFrame):
    """
    Create a bar chart of methodology keyword frequency.

    Extracts keywords from Methodology column and counts occurrences.
    """
    import re
    if "Methodology" not in comparison_df.columns:
        return None
    methodologies = comparison_df["Methodology"].fillna("").astype(str)
    combined = " ".join(methodologies).lower()
    keywords = ["machine learning", "deep learning", "neural", "statistical", "simulation", "survey", "case study"]
    freq = {}
    for kw in keywords:
        c = len(re.findall(r"\b" + re.escape(kw) + r"\b", combined))
        if c > 0:
            freq[kw] = c
    if not freq:
        return None
    df = pd.DataFrame({"Methodology": list(freq.keys()), "Count": list(freq.values())})
    df = df.sort_values("Count", ascending=True)
    fig = px.bar(
        df, x="Count", y="Methodology", orientation="h",
        title="Methodology Frequency Across Papers",
    )
    fig.update_layout(margin=dict(t=50, b=50))
    return fig


def dataset_usage_chart(comparison_df: pd.DataFrame):
    """
    Create a bar chart of dataset keyword frequency.
    """
    import re
    if "Dataset Used" not in comparison_df.columns:
        return None
    datasets = comparison_df["Dataset Used"].fillna("").astype(str)
    combined = " ".join(datasets).lower()
    keywords = ["imagenet", "mnist", "coco", "benchmark", "dataset", "corpus", "evaluation"]
    freq = {}
    for kw in keywords:
        c = len(re.findall(r"\b" + re.escape(kw) + r"\b", combined))
        if c > 0:
            freq[kw] = c
    if not freq:
        return None
    df = pd.DataFrame({"Dataset/Keyword": list(freq.keys()), "Count": list(freq.values())})
    df = df.sort_values("Count", ascending=True)
    fig = px.bar(
        df, x="Count", y="Dataset/Keyword", orientation="h",
        title="Dataset/Evaluation Usage Across Papers",
    )
    fig.update_layout(margin=dict(t=50, b=50))
    return fig


def generate_trend_graphs(comparison_df: pd.DataFrame) -> dict:
    """
    Generate all trend graphs from the comparison DataFrame.

    Returns
    -------
    dict
        Keys: 'papers_by_year', 'methodology', 'dataset'. Values are Plotly figures or None.
    """
    return {
        "papers_by_year": papers_by_year_chart(comparison_df),
        "methodology": methodology_frequency_chart(comparison_df),
        "dataset": dataset_usage_chart(comparison_df),
    }
