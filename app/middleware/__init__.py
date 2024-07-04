"""Initialization module for the authentication middleware package.

This package includes middleware for handling JWT authentication
in FastAPI applications.

Modules:
--------
middleware.py:
    Contains the JWTAuthMiddleware class, which is used to authenticate
    requests using JSON Web Tokens (JWT). The middleware verifies the
    presence and validity of JWT tokens in the Authorization header
    for protected routes.

Classes:
--------
JWTAuthMiddleware:
    Middleware class for JWT authentication.

"""
