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

# Comprehensive debugging
RUN echo "=== FILES COPIED ===" && ls -la
RUN echo "=== PYTHON FILES ===" && find . -name "*.py" -exec echo "File: {}" \; -exec head -5 {} \; -exec echo "---" \;
RUN echo "=== TESTING PYTHON IMPORTS ONE BY ONE ===" && \
    python -c "print('Testing basic imports...')" && \
    python -c "import sys; print('Python path:', sys.path)" && \
    python -c "print('Testing FastAPI import...'); from fastapi import FastAPI; print('FastAPI: OK')" && \
    python -c "print('Testing ChatBot import...'); from ChatBot import ChatBot; print('ChatBot: OK')" || echo "ChatBot import FAILED" && \
    python -c "print('Testing main import...'); import main; print('main: OK')" || echo "main import FAILED"

# Create a detailed startup script for runtime debugging
RUN echo '#!/bin/bash
echo "=== RUNTIME DEBUG ==="
echo "Current directory: $(pwd)"
echo "Files present:"
ls -la
echo ""
echo "Python version: $(python --version)"
echo "Python path:"
python -c "import sys; [print(p) for p in sys.path]"
echo ""
echo "Testing imports step by step:"
python -c "
try:
    print(\"1. Testing FastAPI import...\")
    from fastapi import FastAPI
    print(\"   FastAPI: OK\")
except Exception as e:
    print(f\"   FastAPI: FAILED - {e}\")

try:
    print(\"2. Testing ChatBot import...\")
    from ChatBot import ChatBot
    print(\"   ChatBot: OK\")
except Exception as e:
    print(f\"   ChatBot: FAILED - {e}\")

try:
    print(\"3. Testing main module import...\")
    import main
    print(\"   main: OK\")
except Exception as e:
    print(f\"   main: FAILED - {e}\")
    
try:
    print(\"4. Testing app import from main...\")
    from main import app
    print(\"   app: OK\")
except Exception as e:
    print(f\"   app: FAILED - {e}\")
"
echo ""
echo "Starting uvicorn with verbose output..."
uvicorn main:app --host 0.0.0.0 --port $PORT --log-level debug
' > /app/start_debug.sh && chmod +x /app/start_debug.sh

# Set environment variables
ENV PYTHONPATH=/app

# Use debug startup script
CMD ["/app/start_debug.sh"]