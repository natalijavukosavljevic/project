# Use the official Python image from the Docker Hub
FROM python:3.11


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






