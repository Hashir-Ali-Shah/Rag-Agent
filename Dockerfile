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

# Debug: Show what files exist
RUN echo "=== Files in /app ===" && ls -la

# Debug: Try to import main module
RUN echo "=== Testing Python import ===" && python -c "import main; print('main.py imports successfully')" || echo "Failed to import main.py"

# Debug: Check if app variable exists
RUN echo "=== Testing app variable ===" && python -c "from main import app; print('app variable found:', type(app))" || echo "Failed to import app from main"

# Debug: Show Python version and installed packages
RUN echo "=== Python version ===" && python --version
RUN echo "=== Installed packages ===" && pip list

# Set environment variables
ENV PYTHONPATH=/app

# Create a test script to debug at runtime
RUN echo '#!/bin/bash\necho "=== Runtime Debug ==="\necho "Current directory: $(pwd)"\necho "Files in directory:"\nls -la\necho "Python path:"\npython -c "import sys; print(sys.path)"\necho "Testing main import:"\npython -c "import main; print(\"main imported successfully\")" || echo "Failed to import main"\necho "Starting uvicorn..."\nuvicorn main:app --host 0.0.0.0 --port $PORT' > /app/debug_start.sh && chmod +x /app/debug_start.sh

# Use the debug script instead of direct uvicorn
CMD ["/app/debug_start.sh"]