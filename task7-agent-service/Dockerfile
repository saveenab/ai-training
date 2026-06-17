# ---------- Stage 1: Builder ----------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system build tools needed to compile psycopg2 and faiss-cpu
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (Docker layer caching optimization)
COPY requirements.txt .

# Install dependencies into a clean target directory
RUN pip install --no-cache-dir --target=/install -r requirements.txt

# ---------- Stage 2: Runtime ----------
FROM python:3.12-slim AS runtime

WORKDIR /app

# Create a non-root user to run the application
RUN useradd --create-home --shell /bin/bash appuser

# Copy only the installed dependencies from the builder stage (no build tools)
COPY --from=builder /install /usr/local/lib/python3.12/site-packages

# Install the PostgreSQL client library needed at runtime by psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy application code (changes most often, so this layer is last)
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
