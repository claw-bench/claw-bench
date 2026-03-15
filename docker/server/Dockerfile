# Claw Bench Server — multi-user deployment image
# Designed for 200 concurrent users

FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git jq && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first for layer caching
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[server]" 2>/dev/null || true

# Copy source
COPY . .
RUN pip install --no-cache-dir -e ".[server]"

# Create directories
RUN mkdir -p /var/claw-bench/cache /var/claw-bench/results /app/data/results /app/data/skills-gain /app/data/moltbook

# Non-root user
RUN useradd -m -s /bin/bash clawbench && \
    chown -R clawbench:clawbench /app /var/claw-bench
USER clawbench

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run with uvicorn — 4 workers for multi-core utilization
CMD ["uvicorn", "claw_bench.server.app:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--limit-concurrency", "250", \
     "--timeout-keep-alive", "30"]
