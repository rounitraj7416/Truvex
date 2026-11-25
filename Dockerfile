FROM python:3.12-slim AS builder

# Install build dependencies (needed for psycopg2-binary on some platforms)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first for Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Production stage ---
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN addgroup --system truvex && adduser --system --group truvex

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code
COPY . .

# Create temp directories
RUN mkdir -p temp_audio uploads && chown -R truvex:truvex /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER truvex

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
