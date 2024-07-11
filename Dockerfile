# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update \
    && apt-get install -y libpq-dev

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3

# Set environment variables
ENV DATABASE_URL=${DATABASE_URL}
ENV S3_BUCKET_1=${S3_BUCKET_1}
ENV S3_BUCKET_2=${S3_BUCKET_2}
ENV S3_BUCKET_3=${S3_BUCKET_3}
ENV JWT_SECRET_KEY=${JWT_SECRET_KEY}
ENV JWT_REFRESH_SECRET_KEY=${JWT_REFRESH_SECRET_KEY}

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

# Add the command to run Alembic migrations and start the FastAPI server
# Run Alembic migrations and then start the FastAPI server
CMD ["bash", "-c", "poetry run alembic upgrade head && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]





