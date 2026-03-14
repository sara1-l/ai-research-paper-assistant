import os
from typing import List

import pdfplumber
import pandas as pd


def extract_tables_from_pdf(file_path: str) -> List[pd.DataFrame]:
    """
    Extract tables from a PDF file using pdfplumber and return them
    as a list of pandas DataFrames.

    Parameters
    ----------
    file_path : str
        Path to the PDF file on disk.

    Returns
    -------
    List[pandas.DataFrame]
        A list of DataFrames, one for each detected table. The list may be empty
        if no tables are found or if extraction fails gracefully for all pages.

    Raises
    ------
    FileNotFoundError
        If the provided path does not point to an existing file.
    RuntimeError
        If the PDF cannot be opened or read for any reason.
    """
    if not isinstance(file_path, str) or not file_path.strip():
        raise ValueError("file_path must be a non-empty string.")

    normalized_path = os.path.abspath(file_path)

    if not os.path.isfile(normalized_path):
        raise FileNotFoundError(f"PDF file not found: {normalized_path}")

    dataframes: List[pd.DataFrame] = []

    try:
        with pdfplumber.open(normalized_path) as pdf:
            for page in pdf.pages:
                try:
                    tables = page.extract_tables()
                except Exception:
                    # If one page fails to yield tables, continue with the rest
                    # so we still recover usable data from the document.
                    continue

                for table in tables or []:
                    # `table` is a list of rows; each row is a list of cell strings.
                    if not table:
                        continue

                    # Assume first row as header if it looks header-like (heuristic).
                    header = table[0]
                    body = table[1:] if len(table) > 1 else []

                    try:
                        df = pd.DataFrame(body, columns=header)
                    except Exception:
                        # Fallback: create a DataFrame without headers if shape is inconsistent.
                        df = pd.DataFrame(table)

                    dataframes.append(df)
    except Exception as exc:
        raise RuntimeError(f"Failed to read tables from PDF: {normalized_path}") from exc

    return dataframes

