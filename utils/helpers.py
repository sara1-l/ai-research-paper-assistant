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

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame.

    Returns
    -------
    pandas.DataFrame
        DataFrame with None, NaN, and empty strings replaced by "N/A".
        Numeric columns (e.g., Year, Citations) keep numeric type where
        possible; missing values become "N/A" after fillna.
    """
    if df.empty:
        return df

    result = df.copy()

    for col in result.columns:
        # Fill NaN/None with "N/A"
        result[col] = result[col].fillna("N/A")
        # Replace empty strings
        mask = result[col].astype(str).str.strip() == ""
        result.loc[mask, col] = "N/A"

    return result
