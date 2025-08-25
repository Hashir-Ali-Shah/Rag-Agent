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

# Copy only the backend folder contents to /app
COPY backend/ .

# Debug: Show what files were copied
RUN echo "=== Files copied to /app ===" && ls -la

# Debug: Show Python files specifically
RUN echo "=== Python files ===" && find . -name "*.py" | head -10

# Debug: Test ChatBot import during build
RUN echo "=== Testing ChatBot import during build ===" && \
    python -c "from ChatBot import ChatBot; print('ChatBot imported successfully')" || \
    echo "FAILED: Could not import ChatBot"

# Debug: Test main import during build  
RUN echo "=== Testing main import during build ===" && \
    python -c "import main; print('main imported successfully')" || \
    echo "FAILED: Could not import main"

# Set environment variables
ENV PYTHONPATH=/app

# Start with debugging command that will show runtime info
CMD ["sh", "-c", "echo 'Runtime Debug:' && ls -la && echo 'Testing Python imports:' && python -c 'import main; print(\"Imports OK\")' && echo 'Starting uvicorn...' && uvicorn main:app --host 0.0.0.0 --port $PORT --log-level debug"]