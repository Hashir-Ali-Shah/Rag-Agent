# Use slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only requirements first (for caching)
COPY requirements.txt .

# Install system dependencies and Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ \
        libpq-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y build-essential gcc g++ \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy the rest of the project code
COPY . .

# Change working directory to backend
WORKDIR /app/backend
ENV PYTHONPATH=/app/backend

# Start FastAPI with uvicorn (now pointing directly to main.py)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]