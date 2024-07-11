# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update \
    && apt-get install -y libpq-dev

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3

# Install Poetry and configure it to use virtualenvs in the project directory
RUN pip install "poetry==$POETRY_VERSION" && poetry config virtualenvs.in-project false

# Create a directory for the app
WORKDIR /app/

# Copy the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock /app/

# Install the project dependencies (including dev dependencies for testing)
RUN poetry install --no-root

# Copy the rest of the application code
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Run Alembic migrations and then start the FastAPI server
CMD ["bash", "-c", "poetry run alembic upgrade head && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]






