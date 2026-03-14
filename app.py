from pathlib import Path

import pandas as pd
import requests
import streamlit as st
from streamlit_lottie import st_lottie

from ai_models.summarizer import summarize_text
from pdf_processing.extract_tables import extract_tables_from_pdf
from pdf_processing.extract_text import extract_text_from_pdf
from research_search.semantic_search import search_research_papers
from research_workspace.workspace import (
    extract_texts_from_paths,
    generate_combined_summary,
    get_comparison_table,
    get_trend_graphs,
    get_research_gap_analysis,
    analyze_current_paper_context,
)
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
# RESEARCH PAPER SEARCH SECTION
# -----------------------------
st.markdown("---")
st.subheader("🔍 Research Paper Search")
st.markdown("Search for research papers online in real-time using the Semantic Scholar API.")
st.markdown("<br>", unsafe_allow_html=True)

col_input, col_btn = st.columns([3, 1])
with col_input:
    search_query = st.text_input(
        "Enter Research Topic",
        placeholder="e.g., groundwater contamination, machine learning, climate change",
        label_visibility="collapsed",
        key="search_query",
    )
with col_btn:
    search_clicked = st.button("Search Papers", type="primary", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

if search_clicked:
    if not search_query or not search_query.strip():
        st.warning("Please enter a research topic.")
    else:
        with st.spinner("Fetching research papers..."):
            try:
                df_papers = search_research_papers(search_query.strip())
            except Exception:
                st.error("Error fetching research papers.")
            else:
                if df_papers.empty:
                    st.info("No research papers found.")
                else:
                    st.dataframe(
                        df_papers,
                        use_container_width=True,
                        column_config={
                            "Title": st.column_config.TextColumn("Title", width="large"),
                            "Authors": st.column_config.TextColumn("Authors", width="medium"),
                            "Year": st.column_config.NumberColumn("Year", format="%d"),
                            "Citations": st.column_config.NumberColumn("Citations", format="%d"),
                            "URL": st.column_config.LinkColumn("URL", display_text="Open Paper"),
                        },
                        hide_index=True,
                    )
                    st.caption(f"Found {len(df_papers)} papers. Click **Open Paper** to view the research.")

st.markdown("---")

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
    if "workflow_mode" not in st.session_state:
        st.session_state.workflow_mode = None
    if "research_papers" not in st.session_state:
        st.session_state.research_papers = []
    if st.session_state.last_uploaded_file != uploaded_file.name:
        st.session_state.last_uploaded_file = uploaded_file.name
        st.session_state.summary = None
        st.session_state.workflow_mode = None
        st.session_state.research_papers = []

    st.success("✓ PDF uploaded successfully.")
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
    # VIEW MODE vs RESEARCH MODE
    # -----------------------------
    if st.session_state.workflow_mode is None:
        st.markdown("---")
        st.subheader("What would you like to do?")
        col_v, col_r = st.columns(2)
        with col_v:
            if st.button("1️⃣ View Paper", type="primary", use_container_width=True, key="btn_view"):
                st.session_state.workflow_mode = "view"
                st.rerun()
        with col_r:
            if st.button("2️⃣ Research With Papers", type="primary", use_container_width=True, key="btn_research"):
                st.session_state.workflow_mode = "research"
                st.rerun()

    elif st.session_state.workflow_mode == "view":
        # -----------------------------
        # VIEW PAPER MODE - Tabs
        # -----------------------------
        if st.button("← Back to mode selection", key="back_view"):
            st.session_state.workflow_mode = None
            st.rerun()
        st.markdown("---")
        st.markdown('<p class="section-title">📋 View Paper</p>', unsafe_allow_html=True)
        view_tabs = st.tabs(["📄 Extracted Text", "🧠 Summary", "📊 Tables", "📈 Graphs"])

        with view_tabs[0]:
            st.subheader("Extracted Paper Text")
            st.text_area("Paper Content", full_text[:5000], height=400, label_visibility="collapsed", key="extracted_text")

        with view_tabs[1]:
            st.subheader("AI Generated Summary")
            if not full_text:
                st.info("No text available for summarization.")
            else:
                if "summary" not in st.session_state:
                    st.session_state.summary = None
                if st.button("Generate Summary", type="primary", key="gen_sum_view"):
                    with st.spinner("🤖 AI analyzing the research paper..."):
                        try:
                            structured = summarize_text(full_text)
                            st.session_state.summary = structured
                            st.toast("✅ Analysis complete!", icon="✅")
                        except Exception as e:
                            st.error(f"Failed: {e}")
                structured = st.session_state.summary
                if structured:
                    st.markdown("**Problem**"); st.write(structured.get("problem", ""))
                    st.markdown("**Methodology**"); st.write(structured.get("methodology", ""))
                    st.markdown("**Results**"); st.write(structured.get("results", ""))
                    st.markdown("**Conclusion**"); st.write(structured.get("conclusion", ""))

        with view_tabs[2]:
            st.subheader("Detected Tables")
            if tables:
                for i, table in enumerate(tables):
                    st.markdown(f'<div class="table-card"><strong>Table {i + 1}</strong></div>', unsafe_allow_html=True)
                    st.dataframe(table, use_container_width=True)
            else:
                st.info("No tables found.")

        with view_tabs[3]:
            st.subheader("Automatic Graph Generation")
            if tables:
                df_t = tables[0]
                try:
                    mpl_figs = generate_matplotlib_charts(df_t)
                    plotly_figs = generate_plotly_charts(df_t)
                except ValueError:
                    mpl_figs, plotly_figs = {}, {}
                g1, g2 = st.columns(2)
                with g1:
                    if "line" in plotly_figs:
                        st.plotly_chart(plotly_figs["line"], use_container_width=True)
                    elif "line" in mpl_figs:
                        st.pyplot(mpl_figs["line"])
                    if "pie" in plotly_figs:
                        st.plotly_chart(plotly_figs["pie"], use_container_width=True)
                    elif "pie" in mpl_figs:
                        st.pyplot(mpl_figs["pie"])
                with g2:
                    if "bar" in plotly_figs:
                        st.plotly_chart(plotly_figs["bar"], use_container_width=True)
                    elif "bar" in mpl_figs:
                        st.pyplot(mpl_figs["bar"])
            else:
                st.info("No tables for graphs.")

    elif st.session_state.workflow_mode == "research":
        # -----------------------------
        # RESEARCH WORKSPACE
        # -----------------------------
        if st.button("← Back to mode selection", key="back_research"):
            st.session_state.workflow_mode = None
            st.rerun()
        st.markdown("---")
        st.title("Research Workspace")
        st.markdown("Conduct multi-paper analysis. Upload up to 5 supporting papers.")

        ws_tabs = st.tabs([
            "📤 Upload Papers", "📝 Combined Summary", "📊 Comparison Table",
            "📈 Trend Graphs", "🔬 Research Gap", "📄 Current Paper Analysis",
        ])

        with ws_tabs[0]:
            st.subheader("Upload Supporting Research Papers (Max: 5 PDFs)")
            supporting = st.file_uploader(
                "Upload PDFs",
                type=["pdf"],
                accept_multiple_files=True,
                key="supporting_pdfs",
            )
            if supporting and len(supporting) > 5:
                st.warning("Maximum 5 papers allowed. Only the first 5 will be used.")
                supporting = supporting[:5]
            if supporting:
                paths = [save_uploaded_pdf(f) for f in supporting]
                st.session_state.research_papers = [str(p) for p in paths]
                st.success(f"{len(supporting)} supporting paper(s) uploaded.")
            else:
                st.session_state.research_papers = []

        all_paper_paths = [str(pdf_path)] + (st.session_state.get("research_papers") or [])
        total_papers = len(all_paper_paths)

        if total_papers < 2:
            st.warning("Upload at least 2 papers (current + 1 supporting) for research analysis.")
        else:
            papers_data = extract_texts_from_paths(all_paper_paths)
            current_title = Path(pdf_path).stem.replace("_", " ").replace("-", " ")

            with ws_tabs[1]:
                st.subheader("Combined Summary")
                if st.button("Generate Combined Summary", key="gen_combined"):
                    with st.spinner("Generating summaries for all papers..."):
                        try:
                            paper_sums, overall = generate_combined_summary(
                                papers_data, current_paper_title=current_title
                            )
                            st.session_state.combined_summaries = (paper_sums, overall)
                        except Exception as e:
                            st.error(f"Failed: {e}")
                if "combined_summaries" in st.session_state:
                    paper_sums, overall = st.session_state.combined_summaries
                    for ps in paper_sums:
                        st.markdown(ps)
                        st.markdown("---")
                    st.markdown("**Overall Research Summary**")
                    st.write(overall)

            with ws_tabs[2]:
                st.subheader("Comparison Table")
                try:
                    comp_df = get_comparison_table(papers_data, current_paper_title=current_title)
                    st.dataframe(comp_df, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not build table: {e}")

            with ws_tabs[3]:
                st.subheader("Research Trend Graphs")
                try:
                    comp_df = get_comparison_table(papers_data, current_paper_title=current_title)
                    graphs = get_trend_graphs(comp_df)
                    for name, fig in graphs.items():
                        if fig is not None:
                            st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not generate graphs: {e}")

            with ws_tabs[4]:
                st.subheader("Research Gap Analysis")
                if "combined_summaries" in st.session_state:
                    _, overall = st.session_state.combined_summaries
                    summary_texts = [overall] if overall else []
                    for _, text in papers_data:
                        if text and text.strip():
                            summary_texts.append(text[:1500])
                    gap_text = get_research_gap_analysis(summary_texts)
                    st.markdown(gap_text)
                else:
                    st.info("Generate Combined Summary first.")

            with ws_tabs[5]:
                st.subheader("Current Paper Context Analysis")
                other_summaries = []
                if "combined_summaries" in st.session_state:
                    paper_sums, _ = st.session_state.combined_summaries
                    other_summaries = paper_sums[1:] if len(paper_sums) > 1 else []
                ctx = analyze_current_paper_context(full_text, other_summaries)
                st.markdown(ctx)

else:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👆 Upload a research paper above to get started.")
