"""Middleware for JWT authentication."""

import logging
from typing import Awaitable, Callable

from fastapi import Response
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


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
