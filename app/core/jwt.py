"""Helper functions for generating JWT."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from dotenv import load_dotenv
from jose import jwt

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 60 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")


def create_access_token(
    subject: str | Any, expires_delta: int | None = None,  # noqa: ANN401
) -> str:
    """Create an access token."""
    if expires_delta is not None:
        expires_delta = datetime.now(timezone.utc) + expires_delta
    else:
        expires_delta = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    return jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
