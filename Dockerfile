# Use an official Python 3.11 runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install Poetry
RUN pip install poetry

# Copy only the necessary files for dependency installation
COPY pyproject.toml poetry.lock ./

# Install project dependencies
# --no-dev: Don't install packages in [tool.poetry.dev-dependencies]
# --no-interaction: Do not ask any interactive question
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction

# Copy the rest of your project
COPY . .

# Make port 80 available to the world outside this container
EXPOSE 80

# Run your application
CMD cd persona_kdb && poetry run python app.py --update_vectordb

