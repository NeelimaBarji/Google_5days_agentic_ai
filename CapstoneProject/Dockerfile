# DevLoop Agent — Dockerfile
# Packages the Python multi-agent pipeline for containerized execution

FROM python:3.11-slim

# Install system dependencies for OWASP dependency-check and Java detection
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency list first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent source code
COPY agents/       ./agents/
COPY mcp_servers/  ./mcp_servers/
COPY jira-tickets/ ./jira-tickets/
COPY devloop.py    .
COPY .env.example  .

# The backend/ and frontend/ source trees are mounted at runtime via volume
# so that the DevLoop agent can read and write files to the live codebase.

# Environment variables must be supplied at runtime via --env-file or -e flags.
# Never bake secrets into the image.
ENV PROJECT_ROOT=/workspace

ENTRYPOINT ["python", "devloop.py"]
CMD ["run", "PROD-1"]
