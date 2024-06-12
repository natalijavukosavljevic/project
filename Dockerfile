# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Create a directory for the app
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock /app/

# Install the project dependencies (including dev dependencies for testing)
RUN poetry install --no-root

# Copy the rest of the application code and the tests
COPY ./main /app/mainapp
COPY ./tests /app/tests

# Expose the port the app runs on
EXPOSE 8000

# Default command to run the FastAPI application with uvicorn
CMD ["poetry", "run", "uvicorn", "mainapp.main:app", "--host", "0.0.0.0", "--port", "8000"]
