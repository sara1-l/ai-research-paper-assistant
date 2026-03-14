"""
Research trend visual analytics from structured paper data.

Refined extraction for accurate methodology and dataset frequency.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, List

import pandas as pd
import plotly.express as px

# Normalize methodology variants to canonical names for accurate grouping
METHODOLOGY_ALIASES = {
    "rf": "Random Forest",
    "random forest": "Random Forest",
    "random forests": "Random Forest",
    "svm": "Support Vector Machine",
    "support vector machine": "Support Vector Machine",
    "support vector machines": "Support Vector Machine",
    "cnn": "CNN",
    "convolutional neural network": "CNN",
    "convolutional neural networks": "CNN",
    "rnn": "RNN",
    "recurrent neural network": "RNN",
    "lstm": "LSTM",
    "long short-term memory": "LSTM",
    "transformer": "Transformer",
    "transformers": "Transformer",
    "bert": "BERT/Transformer",
    "gpt": "Transformer",
    "deep learning": "Deep Learning",
    "neural network": "Neural Network",
    "neural networks": "Neural Network",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "regression": "Regression",
    "linear regression": "Regression",
    "logistic regression": "Logistic Regression",
    "classification": "Classification",
    "clustering": "Clustering",
    "k-means": "Clustering",
    "decision tree": "Decision Tree",
    "gradient boosting": "Gradient Boosting",
    "xgboost": "Gradient Boosting",
    "statistical": "Statistical Analysis",
    "simulation": "Simulation",
    "survey": "Survey",
    "case study": "Case Study",
    "experiment": "Experiment",
    "reinforcement learning": "Reinforcement Learning",
    "rl": "Reinforcement Learning",
}

# Normalize dataset names for accurate grouping
DATASET_ALIASES = {
    "imagenet": "ImageNet",
    "mnist": "MNIST",
    "coco": "COCO",
    "squad": "SQuAD",
    "glue": "GLUE",
    "uci": "UCI",
    "kaggle": "Kaggle",
    "benchmark": "Benchmark Dataset",
    "custom": "Custom Dataset",
    "synthetic": "Synthetic Data",
    "satellite": "Satellite/Remote Sensing",
    "remote sensing": "Satellite/Remote Sensing",
    "groundwater": "Groundwater Dataset",
}


def _extract_methodology_terms(structured_papers: List[dict[str, Any]]) -> Counter:
    """Extract and normalize methodology keywords from multiple fields."""
    # Use methodology, key_results, and research_problem for better coverage
    texts = []
    for p in structured_papers:
        for field in ("methodology", "key_results", "research_problem"):
            val = p.get(field, "") or ""
            if val and val != "N/A":
                texts.append(val)
    combined = " ".join(texts).lower()

    counts = Counter()
    for alias, canonical in METHODOLOGY_ALIASES.items():
        # Match whole words; handle multi-word patterns
        pattern = r"\b" + re.escape(alias) + r"\b"
        c = len(re.findall(pattern, combined))
        if c > 0:
            counts[canonical] = counts.get(canonical, 0) + c

    # Merge overlapping categories (e.g., Deep Learning includes Neural Network)
    if counts.get("Deep Learning", 0) > 0 and counts.get("Neural Network", 0) > 0:
        counts["Deep Learning"] += counts["Neural Network"]
        del counts["Neural Network"]
    return counts


def _extract_dataset_terms(structured_papers: List[dict[str, Any]]) -> Counter:
    """Extract and normalize dataset mentions for accurate distribution."""
    counts = Counter()
    not_specified = 0

    for p in structured_papers:
        d = (p.get("dataset_used", "") or "").strip()
        if not d or d == "N/A" or len(d) < 3:
            not_specified += 1
            continue

        # Normalize known datasets
        d_lower = d.lower()
        matched = False
        for alias, canonical in DATASET_ALIASES.items():
            if alias in d_lower:
                counts[canonical] += 1
                matched = True
                break

        if not matched:
            # Use first meaningful phrase (before comma/semicolon)
            parts = re.split(r"[,;]|\band\b", d)
            primary = parts[0].strip()[:60] if parts else d[:60]
            if primary and len(primary) > 4:
                counts[primary] += 1
            else:
                not_specified += 1

    if not_specified > 0 and (not counts or sum(counts.values()) < len(structured_papers)):
        counts["Not specified"] = not_specified

    return counts


def methodology_frequency_bar(structured_papers: List[dict[str, Any]]):
    """Create bar chart of methodology frequency (sorted by count)."""
    counts = _extract_methodology_terms(structured_papers)
    if not counts:
        return None
    sorted_items = counts.most_common(12)
    df = pd.DataFrame([{"Methodology": k, "Count": v} for k, v in sorted_items])
    if df.empty:
        return None
    fig = px.bar(
        df, x="Methodology", y="Count",
        title="Methodology Frequency Across Papers",
        labels={"Count": "Occurrences"},
        text="Count",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_tickangle=-45,
        margin=dict(t=50, b=120),
        yaxis_title="Number of Mentions",
        showlegend=False,
        xaxis={"categoryorder": "total descending"},
    )
    return fig


def dataset_distribution_pie(structured_papers: List[dict[str, Any]]):
    """Create pie chart of dataset distribution with accurate labels."""
    counts = _extract_dataset_terms(structured_papers)
    if not counts:
        return None
    sorted_items = counts.most_common(10)
    df = pd.DataFrame([{"Dataset": k, "Count": v} for k, v in sorted_items])
    if df.empty:
        return None
    fig = px.pie(
        df, values="Count", names="Dataset",
        title="Dataset Usage Distribution Across Papers",
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        margin=dict(t=50, b=20),
        uniformtext_minsize=10,
        uniformtext_mode="hide",
    )
    return fig


def generate_trend_charts(structured_papers: List[dict[str, Any]]) -> dict:
    """
    Generate methodology bar chart and dataset pie chart.

    Returns
    -------
    dict
        Keys: methodology_bar, dataset_pie. Values are Plotly figures or None.
    """
    return {
        "methodology_bar": methodology_frequency_bar(structured_papers),
        "dataset_pie": dataset_distribution_pie(structured_papers),
    }
