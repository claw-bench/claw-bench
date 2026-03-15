FROM python:3.12-slim

LABEL maintainer="Claw Bench Contributors"
LABEL description="Base image for claw-bench task execution"

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install common system tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    jq \
    unzip \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install common Python packages used across tasks
RUN pip install --no-cache-dir \
    pytest>=8 \
    pytest-json-report \
    pydantic>=2 \
    httpx>=0.27 \
    rich>=13

WORKDIR /workspace

CMD ["bash"]
