"""
Helper functions for data formatting and UI display.
"""

from __future__ import annotations

from typing import Any, List

import pandas as pd


def format_authors(authors: List[Any]) -> str:
    """
    Convert a list of author objects to a comma-separated string of names.

    Parameters
    ----------
    authors : list
        List of author objects from API. Each object may have a "name" key
        (e.g., {"name": "John Doe", "authorId": "..."}).

    Returns
    -------
    str
        Comma-separated author names. Returns "N/A" if the list is empty
        or no valid names are found.
    """
    if not authors:
        return "N/A"

    names: List[str] = []
    for author in authors:
        if isinstance(author, dict) and "name" in author:
            name = author["name"]
            if name and str(name).strip():
                names.append(str(name).strip())
        elif isinstance(author, str) and author.strip():
            names.append(author.strip())

    if not names:
        return "N/A"
    return ", ".join(names)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace missing or empty values in a DataFrame with "N/A".

    Text columns use the string "N/A". Numeric columns keep numeric dtypes
    with NaN for missing values so Streamlit NumberColumn and charts work.
    """
    if df.empty:
        return df

    result = df.copy()

    # These columns must stay numeric (NaN when missing) for Streamlit NumberColumn.
    # They often arrive as object dtype from JSON (mixed None/int/str), so do not rely
    # on is_numeric_dtype alone — fillna("N/A") would break int64 formatting.
    _numeric_names = frozenset({"Year", "Citations"})

    for col in result.columns:
        if col in _numeric_names or pd.api.types.is_numeric_dtype(result[col]):
            result[col] = pd.to_numeric(result[col], errors="coerce")
            continue
        result[col] = result[col].fillna("N/A")
        mask = result[col].astype(str).str.strip() == ""
        result.loc[mask, col] = "N/A"

    return result
