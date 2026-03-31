from __future__ import annotations

import os

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from database.models import Base


def get_database_url() -> str | None:
    url = os.getenv("DATABASE_URL", "").strip()
    return url or None


def get_engine() -> Engine:
    url = get_database_url()
    if not url:
        raise RuntimeError("DATABASE_URL is not set.")
    return create_engine(url, pool_pre_ping=True)


def init_db(engine: Engine) -> None:
    """Create all application tables (users + rag_chunks). Requires pgvector on Postgres."""
    Base.metadata.create_all(engine)


def init_user_tables(engine: Engine) -> None:
    """
    Create public.users if missing.

    Supabase's transaction pooler (port 6543) often blocks or breaks DDL. If this
    raises, run scripts/create_users_table.sql in the SQL Editor or use the direct
    DB URL (port 5432) in DATABASE_URL.
    """
    stmts = [
        """
        CREATE TABLE IF NOT EXISTS public.users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """,
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON public.users (email)",
    ]
    try:
        with engine.begin() as conn:
            for stmt in stmts:
                conn.execute(text(stmt))
    except Exception as exc:
        raise RuntimeError(
            "Could not create public.users. If you use Supabase pooling (port 6543), "
            "open scripts/create_users_table.sql, run it in Supabase SQL Editor, then try again. "
            "Alternatively set DATABASE_URL to the direct Postgres connection (port 5432). "
            f"Original error: {exc}"
        ) from exc
