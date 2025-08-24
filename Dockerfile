FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency file
COPY pyproject.toml .

# Install dependencies using Poetry
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy backend source code
COPY backend/ ./backend/

# Set working directory to backend
WORKDIR /app/backend

# Run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
