"""Helper functions for generating JWT."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Awaitable, Callable

from dotenv import load_dotenv
from fastapi import Response  # noqa: TCH002
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request  # noqa: TCH002

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 60 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    """Hashes a plain text password.

    Args:
    ----
        password (str): The plain text password to hash.

    Returns:
    -------
        str: The hashed password.

    """
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    """Verify a plain text password against a hashed password.

    Args:
    ----
        password (str): The plain text password to verify.
        hashed_pass (str): The hashed password to verify against.

    Returns:
    -------
        bool: True if the password matches the hashed password,
        False otherwise.

    """
    return password_context.verify(password, hashed_pass)


def create_access_token(
    subject: str | Any,  # noqa: ANN401
    expires_delta: int | None = None,
) -> str:
    """Create an access token.

    Args:
    ----
        subject (Union[str, Any]): The subject
        (typically user identifier) of the token.
        expires_delta (int, optional): The expiration time delta in seconds.
        Default is None.

    Returns:
    -------
        str: The encoded JWT access token.

    """
    if expires_delta is not None:
        expires_delta = datetime.now(timezone.utc) + expires_delta
    else:
        expires_delta = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    return jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)


def create_refresh_token(
    subject: str | Any,  # noqa: ANN401
    expires_delta: int | None = None,
) -> str:
    """Create a refresh token.

    Args:
    ----
        subject (Union[str, Any]): The subject (typically user identifier)
        of the token.
        expires_delta (int, optional): The expiration time delta in seconds.
          Default is None.

    Returns:
    -------
        str: The encoded JWT refresh token.

    """
    if expires_delta is not None:
        expires_delta = datetime.now(timezone.utc) + expires_delta
    else:
        expires_delta = datetime.now(timezone.utc) + timedelta(
            minutes=REFRESH_TOKEN_EXPIRE_MINUTES,
        )
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    return jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Middleware for JWT authentication.

    Args:
    ----
        app: The ASGI application.
        secret_key (str): The secret key to decode the JWT token.
        algorithm (str): The algorithm used to decode the JWT token.
        protected_routes (list): A list of routes that require authentication.

    Attributes:
    ----------
        logger (logging.Logger): Logger instance for the middleware.

    """

    def __init__(self, app : Callable, secret_key: str, algorithm: str,    # noqa: ANN101
                 protected_routes: list ) -> None:
        """Initialize the JWTAuthMiddleware.

        Args:
        ----
            app: The ASGI application.
            secret_key (str): The secret key to decode the JWT token.
            algorithm (str): The algorithm used to decode the JWT token.
            protected_routes (list): A list of routes
            that require authentication.

        """
        super().__init__(app)
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.protected_routes = protected_routes
        self.logger = logging.getLogger("JWTAuthMiddleware")

    async def dispatch(self, request: Request, call_next: Callable[[Request],  # noqa: ANN101
    Awaitable[Response]]) -> Response:
        """Dispatche the request, checking for a valid JWT token of protected.

        Args:
        ----
            request (Request): The incoming request.
            call_next: The next middleware or route handler.

        Returns:
        -------
            Response: The response from the next middleware or route handler.

        Raises:
        ------
            HTTPException: If the token is missing or invalid.

        """
        if any(
            request.url.path.startswith(route)
            for route in self.protected_routes
        ):
            authorization: str = request.headers.get("Authorization")

            if not authorization or not authorization.startswith("Bearer "):
                self.logger.error("Missing or invalid Authorization header")
                return JSONResponse(
                    content="Missing or invalid Authorization header",
                    status_code=401,
                )

            token = authorization.split(" ")[1]
            try:
                payload = jwt.decode(
                    token, self.secret_key, algorithms=[self.algorithm],
                )
                request.state.user = payload
            except JWTError:
                self.logger.error("Invalid token")  # noqa: TRY400
                return JSONResponse(content="Invalid token", status_code=401)

        return await call_next(request)
