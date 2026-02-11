FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Create app directory
WORKDIR /app

# Copy requirements
COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

# Install dependencies
RUN uv pip install .

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose default port (not used but good practice)
EXPOSE 5600

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5600/api/0/health || exit 1

# Default command
CMD ["uvx", "mcp-server-activitywatch"]