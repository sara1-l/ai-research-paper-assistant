from __future__ import annotations

import os

import streamlit as st

from auth.service import authenticate_user, register_user
from database.session import get_database_url, get_engine
from utils.database_url_display import summarize_database_url


_AUTH_THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 50%, #f0f4f8 100%) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* Avoid clipping gradient text and first block under Streamlit chrome */
section[data-testid="stMain"],
section.main {
    overflow: visible !important;
}
section[data-testid="stMain"] .block-container,
section.main .block-container {
    max-width: 420px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    padding-top: 3.25rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
    overflow: visible !important;
}

@keyframes authFadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.auth-fade-in {
    animation: authFadeIn 0.6s ease-out forwards;
}

.auth-hero-wrap {
    text-align: center;
    margin: 0 0 1.25rem 0;
    padding: 0.35rem 0 0 0;
}
.auth-hero-title {
    display: block;
    font-size: 1.65rem;
    font-weight: 700;
    line-height: 1.35;
    margin: 0 0 0.5rem 0;
    padding: 0.12em 0 0.08em 0;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
}
.auth-hero-sub {
    font-size: 0.9375rem;
    color: #64748b;
    font-weight: 400;
    line-height: 1.5;
    margin: 0 0 1rem 0;
    padding: 0;
}

.auth-features {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.4rem;
    margin: 0;
    width: 100%;
    box-sizing: border-box;
}
.auth-chip {
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    font-size: 0.62rem;
    font-weight: 600;
    color: #475569;
    padding: 0.4rem 0.35rem;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.75);
    border: 1px solid rgba(226, 232, 240, 0.95);
    box-shadow: 0 2px 10px rgba(99, 102, 241, 0.08);
    line-height: 1.25;
    min-height: 2.5rem;
    box-sizing: border-box;
}
@media (max-width: 380px) {
    .auth-features {
        grid-template-columns: 1fr;
    }
    .auth-chip { min-height: auto; }
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 22px !important;
    padding: 1.35rem 1.4rem 1.5rem !important;
    background: rgba(255, 255, 255, 0.72) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 255, 255, 0.98) !important;
    box-shadow:
        0 1px 2px rgba(15, 23, 42, 0.04),
        0 12px 40px -12px rgba(79, 70, 229, 0.18) !important;
    margin-bottom: 0.35rem !important;
}

[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]:first-of-type {
    margin-bottom: 1.1rem !important;
    padding: 0.3rem !important;
    background: #f1f5f9 !important;
    border-radius: 14px !important;
    border: 1px solid #e2e8f0 !important;
}
[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]:first-of-type [data-testid="column"] {
    padding: 0 0.2rem !important;
}
[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]:first-of-type .stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.5rem 0.65rem !important;
    min-height: 2.55rem !important;
    transition: background 0.2s, color 0.2s, box-shadow 0.2s, border-color 0.2s !important;
}
[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]:first-of-type .stButton > button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.65) !important;
    color: #64748b !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: none !important;
}
[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]:first-of-type .stButton > button[kind="secondary"]:hover {
    background: #ffffff !important;
    border-color: #cbd5e1 !important;
    color: #334155 !important;
}
[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]:first-of-type .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 3px 12px rgba(79, 70, 229, 0.32) !important;
}

div[data-testid="stTextInput"] input {
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
    background: #ffffff !important;
    padding: 0.62rem 0.85rem !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.2) !important;
    outline: none !important;
}
div[data-testid="stTextInput"] label {
    color: #475569 !important;
    font-weight: 600 !important;
    font-size: 0.8125rem !important;
}
div[data-testid="stTextInput"] button {
    border-radius: 0 10px 10px 0 !important;
    border: none !important;
    background: transparent !important;
    color: #94a3b8 !important;
}
div[data-testid="stTextInput"] button:hover {
    color: #6366f1 !important;
    background: rgba(99, 102, 241, 0.06) !important;
}

.stButton > button[kind="primary"] {
    border-radius: 12px !important;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    border: none !important;
    box-shadow: 0 4px 16px rgba(79, 70, 229, 0.32) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 22px rgba(79, 70, 229, 0.4) !important;
}

</style>
"""


def _skip_auth() -> bool:
    return os.getenv("SKIP_AUTH", "").lower() in ("1", "true", "yes")


def database_auth_enabled() -> bool:
    return bool(get_database_url()) and not _skip_auth()


def init_auth_session_state() -> None:
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "user_email" not in st.session_state:
        st.session_state.user_email = None


def is_authenticated() -> bool:
    return st.session_state.get("user_id") is not None


def render_login_register_and_stop() -> None:
    """Show login / register UI and halt the rest of the app."""
    st.markdown(_AUTH_THEME_CSS, unsafe_allow_html=True)

    _, hero_col, _ = st.columns([1, 6, 1])
    with hero_col:
        st.markdown(
            '<div class="auth-fade-in auth-hero-wrap">'
            '<p class="auth-hero-title">AI Research Paper Assistant</p>'
            '<p class="auth-hero-sub">Sign in or register to continue.</p>'
            '<div class="auth-features">'
            '<span class="auth-chip">PDF → text & tables</span>'
            '<span class="auth-chip">Smart summaries</span>'
            '<span class="auth-chip">Multi-paper analysis</span>'
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    if "auth_panel" not in st.session_state:
        st.session_state.auth_panel = "login"

    _, form_col, _ = st.columns([1, 6, 1])
    with form_col:
        try:
            auth_box = st.container(border=True)
        except TypeError:
            auth_box = st.container()

        with auth_box:
            seg_l, seg_r = st.columns(2)
            with seg_l:
                if st.button(
                    "Log in",
                    key="auth_pick_login",
                    use_container_width=True,
                    type="primary" if st.session_state.auth_panel == "login" else "secondary",
                ):
                    if st.session_state.auth_panel != "login":
                        st.session_state.auth_panel = "login"
                        st.rerun()
            with seg_r:
                if st.button(
                    "Register",
                    key="auth_pick_register",
                    use_container_width=True,
                    type="primary" if st.session_state.auth_panel == "register" else "secondary",
                ):
                    if st.session_state.auth_panel != "register":
                        st.session_state.auth_panel = "register"
                        st.rerun()

            if st.session_state.auth_panel == "login":
                le = st.text_input("Email", key="login_email", placeholder="you@example.com")
                lp = st.text_input("Password", type="password", key="login_password")
                if st.button("Continue", type="primary", use_container_width=True, key="btn_login"):
                    try:
                        engine = get_engine()
                    except RuntimeError as e:
                        st.error(str(e))
                    else:
                        try:
                            auth = authenticate_user(engine, le, lp)
                        except RuntimeError as exc:
                            st.error(str(exc))
                        else:
                            if auth is None:
                                st.error("Invalid email or password.")
                            else:
                                uid, uemail = auth
                                st.session_state.user_id = uid
                                st.session_state.user_email = uemail
                                st.rerun()
            else:
                re_ = st.text_input("Email", key="reg_email", placeholder="you@example.com")
                rp1 = st.text_input("Password", type="password", key="reg_password", help="At least 8 characters.")
                rp2 = st.text_input("Confirm password", type="password", key="reg_password2")
                if st.button("Create account", type="primary", use_container_width=True, key="btn_register"):
                    if rp1 != rp2:
                        st.error("Passwords do not match.")
                    else:
                        try:
                            engine = get_engine()
                        except RuntimeError as e:
                            st.error(str(e))
                        else:
                            ok, err = register_user(engine, re_, rp1)
                            if not ok:
                                st.error(err or "Registration failed.")
                            else:
                                st.success("Account created. Switch to **Log in** above.")

    st.stop()


def render_sidebar_account() -> None:
    if not database_auth_enabled() or not is_authenticated():
        return
    with st.sidebar:
        st.markdown("---")
        st.caption("Account")
        st.text(st.session_state.user_email or "")
        _u = get_database_url()
        if _u:
            st.caption(f"DB: {summarize_database_url(_u)}")
        if st.button("Log out", key="btn_logout"):
            st.session_state.user_id = None
            st.session_state.user_email = None
            st.rerun()
