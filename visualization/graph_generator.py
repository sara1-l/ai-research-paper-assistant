from __future__ import annotations

from io import BytesIO
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from matplotlib.figure import Figure
from plotly.graph_objs import Figure as PlotlyFigure


def _coerce_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Try to convert string/object columns that look numeric into real numbers.

    This is important for tables extracted from PDFs, where numeric values
    often arrive as strings (e.g. '72', '94').
    """
    df_converted = df.copy()
    for col in df_converted.columns:
        if df_converted[col].dtype == "object":
            # Attempt to convert; non-numeric values become NaN
            coerced = pd.to_numeric(df_converted[col].str.replace("%", ""), errors="coerce")
            # If we got at least one non-NaN numeric value, treat this as numeric
            if coerced.notna().sum() > 0:
                df_converted[col] = coerced
    return df_converted


def _choose_axes(df_numeric: pd.DataFrame) -> Tuple[Optional[str], List[str]]:
    """
    Heuristically choose x and y columns for plotting.

    Strategy:
    - If there is a "year-like" numeric column (name contains 'year' or
      values are mostly between 1900 and 2100), use it as x.
    - Otherwise, use the DataFrame index as x (return None) and all numeric
      columns as y.
    """
    numeric_cols = _detect_numeric_columns(df_numeric)
    if not numeric_cols:
        return None, []

    # Detect year-like column
    year_col: Optional[str] = None
    for col in numeric_cols:
        name_lower = str(col).lower()
        series = df_numeric[col].dropna()
        if series.empty:
            continue
        if "year" in name_lower:
            year_col = col
            break
        # Check range heuristic
        median_val = series.median()
        if 1900 <= median_val <= 2100:
            year_col = col
            break

    if year_col is not None:
        y_cols = [c for c in numeric_cols if c != year_col]
        # If everything except the year column was filtered out, fall back to all numeric cols
        if not y_cols:
            y_cols = [c for c in numeric_cols if c == year_col]
        return year_col, y_cols

    # Fallback: index on x, all numeric columns as y
    return None, numeric_cols


def _detect_numeric_columns(df: pd.DataFrame) -> List[str]:
    """
    Return a list of numeric column names in the DataFrame.
    """
    return df.select_dtypes(include=["number"]).columns.tolist()


def _detect_categorical_column(df: pd.DataFrame) -> Optional[str]:
    """
    Heuristically pick a categorical column for grouping, if available.
    """
    for col in df.columns:
        if df[col].dtype == "object" or pd.api.types.is_categorical_dtype(df[col]):
            return col
    return None


def generate_matplotlib_charts(df: pd.DataFrame) -> Dict[str, Figure]:
    """
    Generate basic matplotlib charts (line, bar, pie) from a DataFrame.

    Returns
    -------
    Dict[str, matplotlib.figure.Figure]
        Dictionary with keys: 'line', 'bar', 'pie'.
        Some entries may be omitted if a suitable plot cannot be created.
    """
    if df.empty:
        raise ValueError("Cannot generate charts from an empty DataFrame.")

    figures: Dict[str, Figure] = {}

    # Make a numeric-friendly copy first
    df_numeric = _coerce_numeric_columns(df)
    numeric_cols = _detect_numeric_columns(df_numeric)

    if not numeric_cols:
        raise ValueError("No numeric columns found in DataFrame for chart generation.")

    # Choose axes
    x_col, y_cols = _choose_axes(df_numeric)
    x_axis = df_numeric.index if x_col is None else df_numeric[x_col]

    # Line chart: trends over chosen x-axis
    fig_line, ax_line = plt.subplots()
    for col in y_cols:
        ax_line.plot(x_axis, df_numeric[col], label=str(col))
    ax_line.set_xlabel("Index" if x_col is None else str(x_col))
    ax_line.set_ylabel("Values")
    ax_line.set_title("Line Chart (Numeric Columns)")
    ax_line.legend(loc="best")
    figures["line"] = fig_line

    # Bar chart: use first y column
    first_numeric = y_cols[0]
    fig_bar, ax_bar = plt.subplots()
    ax_bar.bar(x_axis, df_numeric[first_numeric])
    ax_bar.set_xlabel("Index" if x_col is None else str(x_col))
    ax_bar.set_ylabel(first_numeric)
    ax_bar.set_title(f"Bar Chart ({first_numeric})")
    figures["bar"] = fig_bar

    # Pie chart: requires a categorical column and one numeric column
    cat_col = _detect_categorical_column(df)
    if cat_col is not None:
        # Aggregate numeric column by category
        pie_series = df_numeric.groupby(cat_col)[first_numeric].sum()
        fig_pie, ax_pie = plt.subplots()
        ax_pie.pie(pie_series.values, labels=pie_series.index, autopct="%1.1f%%")
        ax_pie.set_title(f"Pie Chart ({first_numeric} by {cat_col})")
        figures["pie"] = fig_pie

    return figures


def generate_plotly_charts(df: pd.DataFrame) -> Dict[str, PlotlyFigure]:
    """
    Generate basic Plotly charts (line, bar, pie) from a DataFrame.

    Returns
    -------
    Dict[str, plotly.graph_objs.Figure]
        Dictionary with keys: 'line', 'bar', 'pie'.
        Some entries may be omitted if a suitable plot cannot be created.
    """
    if df.empty:
        raise ValueError("Cannot generate charts from an empty DataFrame.")

    figures: Dict[str, PlotlyFigure] = {}

    df_numeric = _coerce_numeric_columns(df)
    numeric_cols = _detect_numeric_columns(df_numeric)

    if not numeric_cols:
        raise ValueError("No numeric columns found in DataFrame for chart generation.")

    x_col, y_cols = _choose_axes(df_numeric)
    x_arg = df_numeric.index if x_col is None else df_numeric[x_col]

    # Line chart
    fig_line = px.line(
        df_numeric,
        x=x_arg,
        y=y_cols,
        title="Line Chart (Numeric Columns)",
    )
    fig_line.update_layout(
        xaxis_title="Index" if x_col is None else str(x_col),
        yaxis_title="Values",
    )
    figures["line"] = fig_line

    # Bar chart: use first y column
    first_numeric = y_cols[0]
    fig_bar = px.bar(
        df_numeric,
        x=x_arg,
        y=first_numeric,
        title=f"Bar Chart ({first_numeric})",
    )
    fig_bar.update_layout(
        xaxis_title="Index" if x_col is None else str(x_col),
        yaxis_title=first_numeric,
    )
    figures["bar"] = fig_bar

    # Pie chart
    cat_col = _detect_categorical_column(df)
    if cat_col is not None:
        pie_df = df_numeric.groupby(cat_col, as_index=False)[first_numeric].sum()
        fig_pie = px.pie(
            pie_df,
            names=cat_col,
            values=first_numeric,
            title=f"Pie Chart ({first_numeric} by {cat_col})",
        )
        figures["pie"] = fig_pie

    return figures


def export_matplotlib_figure_to_png_bytes(fig: Figure, dpi: int = 150) -> bytes:
    """
    Export a matplotlib figure to PNG bytes.

    These bytes can be used with Streamlit's st.image or saved to disk.
    """
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=dpi, bbox_inches="tight")
    buffer.seek(0)
    return buffer.read()


def export_plotly_figure_to_png_bytes(fig: PlotlyFigure, width: int = 800, height: int = 600) -> bytes:
    """
    Export a Plotly figure to PNG bytes.

    Requires the 'kaleido' package to be installed for static image export.
    """
    # Plotly's to_image returns bytes when passed format="png"
    return fig.to_image(format="png", width=width, height=height)


def export_all_charts_to_images(
    mpl_figures: Dict[str, Figure],
    plotly_figures: Dict[str, PlotlyFigure],
) -> Dict[Tuple[str, str], bytes]:
    """
    Export all provided matplotlib and Plotly figures to PNG bytes.

    Returns a dictionary keyed by (backend, chart_type), where backend is
    either 'matplotlib' or 'plotly', and chart_type is 'line', 'bar', or 'pie'.
    """
    images: Dict[Tuple[str, str], bytes] = {}

    for chart_type, fig in mpl_figures.items():
        images[("matplotlib", chart_type)] = export_matplotlib_figure_to_png_bytes(fig)

    for chart_type, fig in plotly_figures.items():
        images[("plotly", chart_type)] = export_plotly_figure_to_png_bytes(fig)

    return images

