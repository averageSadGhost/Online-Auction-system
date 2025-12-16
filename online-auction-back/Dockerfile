# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies (including Pillow requirements)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt


# Production stage
FROM python:3.12-slim

# Create non-root user for security
RUN groupadd -r auction && useradd -r -g auction auction

WORKDIR /app

# Install runtime dependencies (including Pillow requirements)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libjpeg62-turbo \
    zlib1g \
    libpng16-16 \
    libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder stage
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install Python packages
RUN pip install --no-cache /wheels/*

# Copy application code
COPY --chown=auction:auction . .

# Create directories for static, media, data, and log files
RUN mkdir -p /app/staticfiles /app/media /app/logs /app/data \
    && chown -R auction:auction /app/staticfiles /app/media /app/logs /app/data

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Switch to non-root user
USER auction

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health/live/')" || exit 1

# Run entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
