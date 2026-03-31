from __future__ import annotations

import os

import streamlit as st

from auth.service import authenticate_user, register_user
from database.session import get_database_url, get_engine
from utils.database_url_display import summarize_database_url


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
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown("### AI Research Paper Assistant")
        st.caption("Sign in or register. Accounts are stored in Postgres (e.g. Supabase).")
        _dbu = get_database_url()
        if _dbu:
            st.caption(f"App will use: **{summarize_database_url(_dbu)}** (password hidden). Compare this host to your Supabase project.")

    _, form_col, _ = st.columns([1, 2, 1])
    with form_col:
        tab_login, tab_register = st.tabs(["Log in", "Register"])

        with tab_login:
            le = st.text_input("Email", key="login_email", placeholder="you@example.com")
            lp = st.text_input("Password", type="password", key="login_password")
            if st.button("Log in", type="primary", use_container_width=True, key="btn_login"):
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

        with tab_register:
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
                            st.success("Account created. You can log in now.")
                            st.caption(
                                f"Saved to Postgres: **{summarize_database_url(get_database_url())}**. "
                                "In Supabase, open **Table Editor → schema public → users** (not Authentication)."
                            )

        st.caption(
            "Tip: set `DATABASE_URL` to your Supabase connection string. "
            "Use `SKIP_AUTH=1` only for local demos without a database."
        )

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
