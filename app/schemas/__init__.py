"""Initialization module for the schema definitions package.

This package contains Pydantic models and schema definitions for the FastAPI
application, used for data validation, serialization, and documentation.

Modules:
--------
project.py:
    Contains Pydantic models and schemas related to projects, including
    input and output schemas for project operations.
user.py:
    Contains Pydantic models and schemas related to users, including
    input and output schemas for user operations.
image.py:
    Contains Pydantic models and schemas related to images, including
    input and output schemas for image operations.
document.py:
    Contains Pydantic models and schemas related to documents, including
    input and output schemas for document operations.

Schemas:
--------
ProjectCreate:
    Schema for creating a new project.
ProjectOut:
    Schema for project output data.
UserCreate:
    Schema for creating a new user.
UserOut:
    Schema for user output data.
ImageCreate:
    Schema for creating a new image.
ImageOut:
    Schema for image output data.
DocumentCreate:
    Schema for creating a new document.
DocumentOut:
    Schema for document output data.
"""
