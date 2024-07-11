# Use the official Python image from the Docker Hub
FROM python:3.11

# Set environment variables
ENV DATABASE_URL=${DATABASE_URL}
ENV S3_BUCKET_1=${S3_BUCKET_1}
ENV S3_BUCKET_2=${S3_BUCKET_2}
ENV S3_BUCKET_3=${S3_BUCKET_3}
ENV JWT_SECRET_KEY=${JWT_SECRET_KEY}
ENV JWT_REFRESH_SECRET_KEY=${JWT_REFRESH_SECRET_KEY}

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install pipx and poetry
RUN pip install pipx
RUN pipx install poetry

# Install any needed packages specified in poetry.lock and pyproject.toml
RUN poetry install

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run Alembic migrations and then start the FastAPI server
CMD ["bash", "-c", "poetry run alembic upgrade head && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]






