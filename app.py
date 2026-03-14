from pathlib import Path

import pandas as pd
import requests
import streamlit as st
from streamlit_lottie import st_lottie

from ai_models.summarizer import summarize_text
from pdf_processing.extract_tables import extract_tables_from_pdf
from pdf_processing.extract_text import extract_text_from_pdf
from visualization.graph_generator import (
    generate_matplotlib_charts,
    generate_plotly_charts,
    export_all_charts_to_images,
)

st.set_page_config(
    page_title="AI Research Paper Assistant",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# LOTTIE HELPER
# -----------------------------
def load_lottie(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


# -----------------------------
# MODERN AI DASHBOARD CSS
# -----------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Light theme with glassmorphism */
.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 50%, #f0f4f8 100%);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Hide default Streamlit branding for cleaner look */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* Hero section */
.hero-title {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
}

.hero-subtitle {
    font-size: 1.1rem;
    color: #64748b;
    text-align: center;
    font-weight: 400;
    margin-bottom: 2rem;
}

/* Feature cards - glassmorphism */
.feature-card {
    padding: 1.5rem;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.8);
    box-shadow: 0 8px 32px rgba(99, 102, 241, 0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    text-align: center;
}

.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(99, 102, 241, 0.2);
    border-color: rgba(99, 102, 241, 0.3);
}

.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

.feature-label {
    font-weight: 600;
    color: #334155;
    font-size: 0.95rem;
}

/* Upload card */
.upload-card {
    padding: 2.5rem;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.9);
    box-shadow: 0 10px 40px rgba(99, 102, 241, 0.12);
    margin: 2rem auto;
    max-width: 520px;
}

.upload-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #334155;
    text-align: center;
    margin-bottom: 0.5rem;
}

.upload-hint {
    font-size: 0.875rem;
    color: #64748b;
    text-align: center;
    margin-bottom: 1.5rem;
}

/* Dashboard section containers */
.dashboard-section {
    padding: 1.5rem;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.8);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
    margin-bottom: 1.5rem;
}

.section-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Table card styling */
.table-card {
    padding: 1.25rem;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(226, 232, 240, 0.9);
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
    margin-bottom: 1rem;
}

/* Graph card */
.graph-card {
    padding: 1rem;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(226, 232, 240, 0.9);
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
    margin-bottom: 1rem;
}

/* Buttons */
.stButton > button {
    border-radius: 10px;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: white;
    font-weight: 600;
    border: none;
    padding: 0.5rem 1.25rem;
    transition: all 0.2s ease;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
}

/* Success message styling */
.stSuccess {
    border-radius: 10px;
    border-left: 4px solid #10b981;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.fade-in {
    animation: fadeIn 0.6s ease-out forwards;
}

/* Dataframe container - rounded */
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* File uploader styling */
section[data-testid="stFileUploader"] {
    border-radius: 12px;
    padding: 1rem;
    background: rgba(248, 250, 252, 0.8);
    border: 2px dashed #cbd5e1;
}

section[data-testid="stFileUploader"]:hover {
    border-color: #6366f1;
    background: rgba(99, 102, 241, 0.04);
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# HERO SECTION
# -----------------------------
st.markdown(
    """
    <div class="fade-in">
        <h1 class="hero-title">AI Research Paper Assistant</h1>
        <p class="hero-subtitle">Upload a research paper and let AI analyze it automatically</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Lottie animation
lottie_url = "https://assets10.lottiefiles.com/packages/lf20_qp1q7mct.json"
animation = load_lottie(lottie_url)
if animation:
    col_hero1, col_hero2, col_hero3 = st.columns([1, 2, 1])
    with col_hero2:
        st_lottie(animation, height=180, key="hero_lottie")

# -----------------------------
# FEATURE CARDS
# -----------------------------
st.markdown("<br>", unsafe_allow_html=True)
fc1, fc2, fc3, fc4 = st.columns(4)
with fc1:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <div class="feature-label">Extract Text</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with fc2:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-label">AI Summary</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with fc3:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-label">Detect Tables</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with fc4:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <div class="feature-label">Generate Graphs</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# UPLOAD SECTION
# -----------------------------
st.markdown("<br>", unsafe_allow_html=True)
col_upload1, col_upload2, col_upload3 = st.columns([1, 2, 1])
with col_upload2:
    st.markdown(
        """
        <div class="upload-card">
            <div class="upload-title">📤 Upload Research Paper</div>
            <div class="upload-hint">Drop your PDF here or browse. We'll extract text, tables, and generate insights.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        label_visibility="collapsed",
        key="main_uploader",
    )

# -----------------------------
# FILE HANDLING (unchanged backend)
# -----------------------------
DATA_DIR = Path("data") / "papers"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_pdf(uploaded_file) -> Path:
    file_path = DATA_DIR / uploaded_file.name
    uploaded_file.seek(0)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    return file_path


# -----------------------------
# MAIN DASHBOARD (when file uploaded)
# -----------------------------
if uploaded_file:
    if "last_uploaded_file" not in st.session_state:
        st.session_state.last_uploaded_file = None
    if st.session_state.last_uploaded_file != uploaded_file.name:
        st.session_state.last_uploaded_file = uploaded_file.name
        st.session_state.summary = None

    st.success("✓ PDF uploaded successfully. Analyzing document...")
    pdf_path = save_uploaded_pdf(uploaded_file)

    # Backend extraction (unchanged)
    try:
        full_text = extract_text_from_pdf(str(pdf_path))
    except Exception as e:
        st.error(f"Failed to extract text from PDF: {e}")
        full_text = ""

    try:
        tables = extract_tables_from_pdf(str(pdf_path))
    except Exception as e:
        st.error(f"Failed to extract tables from PDF: {e}")
        tables = []

    # -----------------------------
    # TWO-COLUMN DASHBOARD LAYOUT
    # -----------------------------
    st.markdown("---")
    st.markdown(
        '<p class="section-title">📋 Research Dashboard</p>',
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown(
            """
            <div class="dashboard-section">
                <div class="section-title">📄 Extracted Paper Text</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.text_area(
            "Paper Content",
            full_text[:5000],
            height=400,
            label_visibility="collapsed",
            key="extracted_text",
        )

    with col_right:
        st.markdown(
            """
            <div class="dashboard-section">
                <div class="section-title">🧠 AI Summary</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not full_text:
            st.info("No text available for summarization.")
        else:
            if "summary" not in st.session_state:
                st.session_state.summary = None

            if st.button("Generate Summary", type="primary", use_container_width=True):
                with st.spinner("🤖 AI analyzing the research paper..."):
                    try:
                        structured = summarize_text(full_text)
                        st.session_state.summary = structured
                        st.toast("✅ Analysis complete! Summary ready.", icon="✅")
                    except Exception as e:
                        st.error(f"Failed to generate summary: {e}")
                        st.session_state.summary = None

            structured = st.session_state.summary
            if structured:
                    st.markdown("**Problem**")
                    st.write(structured.get("problem", ""))

                    st.markdown("**Methodology**")
                    st.write(structured.get("methodology", ""))

                    st.markdown("**Results**")
                    st.write(structured.get("results", ""))

                    st.markdown("**Conclusion**")
                    st.write(structured.get("conclusion", ""))

    # -----------------------------
    # TABLES SECTION (styled cards)
    # -----------------------------
    st.markdown("---")
    st.markdown(
        '<p class="section-title">📊 Detected Tables</p>',
        unsafe_allow_html=True,
    )

    if tables:
        for i, table in enumerate(tables):
            st.markdown(
                f'<div class="table-card"><strong>Table {i + 1}</strong></div>',
                unsafe_allow_html=True,
            )
            st.dataframe(table, use_container_width=True)
    else:
        st.info("No tables found in this paper.")

    # -----------------------------
    # GRAPHS DASHBOARD (two-column grid)
    # -----------------------------
    st.markdown("---")
    st.markdown(
        '<p class="section-title">📈 Automatic Graph Generation</p>',
        unsafe_allow_html=True,
    )

    if not tables:
        st.info("Upload a paper containing tables to generate graphs.")
    else:
        df: pd.DataFrame = tables[0]
        st.caption("Source: Table 1")
        st.dataframe(df, use_container_width=True)

        try:
            mpl_figs = generate_matplotlib_charts(df)
            plotly_figs = generate_plotly_charts(df)
        except ValueError as e:
            st.warning(str(e))
            mpl_figs, plotly_figs = {}, {}

        # Two-column grid for Plotly charts
        g1, g2 = st.columns(2)

        with g1:
            if "line" in plotly_figs:
                st.markdown('<div class="graph-card">**Line Chart**</div>', unsafe_allow_html=True)
                st.plotly_chart(plotly_figs["line"], use_container_width=True)
            elif "line" in mpl_figs:
                st.markdown('<div class="graph-card">**Line Chart**</div>', unsafe_allow_html=True)
                st.pyplot(mpl_figs["line"])

            if "pie" in plotly_figs:
                st.markdown('<div class="graph-card">**Pie Chart**</div>', unsafe_allow_html=True)
                st.plotly_chart(plotly_figs["pie"], use_container_width=True)
            elif "pie" in mpl_figs:
                st.markdown('<div class="graph-card">**Pie Chart**</div>', unsafe_allow_html=True)
                st.pyplot(mpl_figs["pie"])

        with g2:
            if "bar" in plotly_figs:
                st.markdown('<div class="graph-card">**Bar Chart**</div>', unsafe_allow_html=True)
                st.plotly_chart(plotly_figs["bar"], use_container_width=True)
            elif "bar" in mpl_figs:
                st.markdown('<div class="graph-card">**Bar Chart**</div>', unsafe_allow_html=True)
                st.pyplot(mpl_figs["bar"])

        if mpl_figs or plotly_figs:
            if st.checkbox("Show download options for charts"):
                images = export_all_charts_to_images(mpl_figs, plotly_figs)
                for (backend, chart_type), img_bytes in images.items():
                    st.download_button(
                        label=f"Download {backend} {chart_type} chart",
                        data=img_bytes,
                        file_name=f"{backend}_{chart_type}_chart.png",
                        mime="image/png",
                    )

else:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👆 Upload a research paper above to get started.")
