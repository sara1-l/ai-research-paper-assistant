from __future__ import annotations

import re
from typing import Literal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from werkzeug.security import check_password_hash, generate_password_hash

from database.models import User
from database.session import init_user_tables

AuthUserInfo = tuple[int, str]

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_email(email: str) -> bool:
    return bool(_EMAIL_RE.match(_normalize_email(email)))


def register_user(engine: Engine, email: str, password: str) -> tuple[Literal[True], None] | tuple[Literal[False], str]:
    email_n = _normalize_email(email)
    if not validate_email(email_n):
        return False, "Enter a valid email address."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    try:
        init_user_tables(engine)
    except RuntimeError as exc:
        return False, str(exc)

    pw_hash = generate_password_hash(password)

    with Session(engine) as session:
        user = User(email=email_n, password_hash=pw_hash)
        session.add(user)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            return False, "An account with this email already exists."
        except Exception as exc:
            session.rollback()
            return False, f"Registration failed: {exc}"

    return True, None


def authenticate_user(engine: Engine, email: str, password: str) -> AuthUserInfo | None:
    email_n = _normalize_email(email)
    if not email_n or not password:
        return None

    init_user_tables(engine)

    with Session(engine) as session:
        stmt = select(User).where(User.email == email_n)
        user = session.execute(stmt).scalar_one_or_none()
        if user is None:
            return None
        if not check_password_hash(user.password_hash, password):
            return None
        return (user.id, user.email)
