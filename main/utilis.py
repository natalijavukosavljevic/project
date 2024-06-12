"""Helper functions for generating JWT."""
from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from typing import Any

from fastapi import HTTPException, Response
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request  # noqa: TCH002

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]     # should be kept secret
JWT_REFRESH_SECRET_KEY = os.environ["JWT_REFRESH_SECRET_KEY"]

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


def create_access_token(subject: str | Any, expires_delta: int = None,  # noqa: ANN401, RUF013
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
        expires_delta = datetime.utcnow() + expires_delta  # noqa: DTZ003
    else:
        expires_delta = datetime.utcnow() + timedelta( # noqa: DTZ003
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    return jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)

def create_refresh_token(subject: str | Any, expires_delta: int = None,  # noqa: ANN401, RUF013
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
        expires_delta = datetime.utcnow() + expires_delta  # noqa: DTZ003
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes =  # noqa: DTZ003
                                                      REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    return jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)


def verify_token(token: str, credentials_exception : Exception,  # noqa: D417
                 ) -> dict[str, Any]:
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
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return payload  # noqa: TRY300
    except JWTError:
        raise credentials_exception  # noqa: B904

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

    def __init__(self, app, secret_key: str, algorithm: str, # noqa: ANN001, ANN101
                  protected_routes: list) -> None:
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

    async def dispatch(self, request: Request, call_next) -> Response:  # noqa: ANN001, ANN101
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
        if any(request.url.path.startswith(route) for route
               in self.protected_routes):
            authorization: str = request.headers.get("Authorization")

            if not authorization or not authorization.startswith("Bearer "):
                self.logger.error("Missing or invalid Authorization header")
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or missing Authorization header",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            token = authorization.split(" ")[1]
            try:
                payload = jwt.decode(token, self.secret_key,
                                     algorithms=[self.algorithm])
                request.state.user = payload
            except JWTError:
                self.logger.error("Invalid token")  # noqa: TRY400
                raise HTTPException(  # noqa: B904
                    status_code=401,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        return await call_next(request)
