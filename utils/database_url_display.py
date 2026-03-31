from __future__ import annotations

from urllib.parse import unquote, urlparse


def summarize_database_url(url: str | None) -> str:
    """
    Show user@host:port/dbname for debugging (no password).
    Helps confirm the app points at the same Supabase project you open in the dashboard.
    """
    if not url or not str(url).strip():
        return "(DATABASE_URL not set)"
    s = str(url).strip()
    for driver in ("postgresql+psycopg2://", "postgresql://", "postgres://"):
        if s.startswith(driver):
            s = "postgresql://" + s[len(driver) :]
            break
    parsed = urlparse(s)
    if not parsed.hostname:
        return "(could not parse DATABASE_URL)"
    port = f":{parsed.port}" if parsed.port else ""
    db = (parsed.path or "").lstrip("/") or "?"
    user = unquote(parsed.username) if parsed.username else "?"
    return f"{user} @ {parsed.hostname}{port} / {db}"
