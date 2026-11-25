FROM python:3.12-slim

WORKDIR /app

# Install build & PostgreSQL client runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Ensure temp directories exist
RUN mkdir -p temp_audio uploads

# Expose Render default port
EXPOSE 8000

# Run migrations if available and start server
CMD ["sh", "-c", "alembic upgrade head 2>/dev/null || true; exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
