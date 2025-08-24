# Use slim Python image
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ \
        libpq-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y build-essential gcc g++ \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY . .

WORKDIR /app

# Use Render's dynamic port
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
