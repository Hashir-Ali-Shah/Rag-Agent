FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency file first
COPY pyproject.toml .
# If you use requirements.txt instead, copy that and run pip install

# Install dependencies (Poetry or pip)
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy backend folder
COPY backend/ ./backend/

# Set working dir to backend
WORKDIR /app/backend

# Run your app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
