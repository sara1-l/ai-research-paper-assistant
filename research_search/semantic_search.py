"""
Semantic Scholar API integration for research paper search.

This module fetches relevant research papers from the Semantic Scholar
Academic Graph API based on user search queries.

For higher rate limits, set SEMANTICSCHOLAR_API_KEY in your environment
or in Streamlit secrets (.streamlit/secrets.toml).
"""

from __future__ import annotations

import os
import time
from typing import Any, List

import pandas as pd
import requests

from utils.helpers import clean_dataframe, format_authors

# Semantic Scholar API base URL
API_BASE = "https://api.semanticscholar.org/graph/v1"
SEARCH_ENDPOINT = f"{API_BASE}/paper/search"

# Fields to request from the API
FIELDS = "paperId,title,authors,year,citationCount,url"
LIMIT = 10

# Retry config for rate limits (429)
MAX_RETRIES = 3
RETRY_DELAY_SEC = 5


def _get_api_key() -> str | None:
    """Get API key from environment or Streamlit secrets."""
    key = os.environ.get("SEMANTICSCHOLAR_API_KEY", "").strip()
    if key:
        return key
    try:
        import streamlit as st

        sec = st.secrets
        if "SEMANTICSCHOLAR_API_KEY" in sec:
            key = str(sec["SEMANTICSCHOLAR_API_KEY"]).strip()
            if key:
                return key
    except Exception:
        pass
    return None


def search_research_papers(query: str) -> pd.DataFrame:
    """
    Search for research papers using the Semantic Scholar API.

    Parameters
    ----------
    query : str
        Search topic or keywords (e.g., "groundwater contamination").

    Returns
    -------
    pandas.DataFrame
        DataFrame with columns: Title, Authors, Year, Citations, URL.
        Empty DataFrame if the API fails or returns no results.

    Notes
    -----
    The API returns up to 10 papers. Authors are formatted as a
    comma-separated string. Missing values are replaced with "N/A".
    """
    if not query or not str(query).strip():
        return pd.DataFrame(columns=["Title", "Authors", "Year", "Citations", "URL"])

    params = {
        "query": str(query).strip(),
        "limit": LIMIT,
        "fields": FIELDS,
    }

    headers = {"Accept": "application/json"}
    api_key = _get_api_key()
    if api_key:
        headers["x-api-key"] = api_key

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(
                SEARCH_ENDPOINT,
                params=params,
                timeout=15,
                headers=headers,
            )
            if response.status_code == 429:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY_SEC)
                    continue
                raise RuntimeError(
                    "Rate limit exceeded. The Semantic Scholar API allows ~100 requests per 5 minutes without an API key. "
                    "Add SEMANTICSCHOLAR_API_KEY to your environment for higher limits, or try again later."
                )
            response.raise_for_status()
            break
        except requests.RequestException as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                resp = getattr(e, "response", None)
                if resp is not None and getattr(resp, "status_code", None) == 429:
                    time.sleep(RETRY_DELAY_SEC)
                    continue
            raise RuntimeError(
                "Failed to connect to Semantic Scholar API. "
                "Check your internet connection or try again later."
            ) from last_error

    try:
        data = response.json()
    except ValueError:
        raise RuntimeError("Invalid response from Semantic Scholar API.")

    # API returns {"total": N, "offset": 0, "data": [...]}
    papers = data.get("data") or []
    if not papers:
        return pd.DataFrame(columns=["Title", "Authors", "Year", "Citations", "URL"])

    rows: List[dict[str, Any]] = []
    for paper in papers:
        # Build URL: use API url if present, else construct from paperId
        paper_id = paper.get("paperId", "")
        url = paper.get("url") or (
            f"https://www.semanticscholar.org/paper/{paper_id}" if paper_id else "N/A"
        )
        if url and url != "N/A":
            url = str(url)

        rows.append({
            "Title": paper.get("title") or "N/A",
            "Authors": format_authors(paper.get("authors") or []),
            "Year": paper.get("year"),
            "Citations": paper.get("citationCount"),
            "URL": url,
        })

    df = pd.DataFrame(rows)
    return clean_dataframe(df)
