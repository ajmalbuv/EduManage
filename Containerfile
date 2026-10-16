# syntax=docker/dockerfile:1.7

# -----------------------------------------------------------------------------
# Stage 1: Build Virtual Environment with UV
# -----------------------------------------------------------------------------
FROM docker.io/library/python:3.12-slim-bookworm AS builder

# Install uv binary directly from official Astral uv image
COPY --from=ghcr.io/astral-sh/uv:0.5.26 /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation and standalone copy mode
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Cache dependency installations using uv.lock
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# -----------------------------------------------------------------------------
# Stage 2: Minimal Production Runtime
# -----------------------------------------------------------------------------
FROM docker.io/library/python:3.12-slim-bookworm AS runner

WORKDIR /app

# Install curl for Podman container health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create unprivileged application user
RUN groupadd --gid 1000 edumanage && \
    useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash edumanage

# Python & Django environment configuration
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PORT=8000 \
    STATIC_ROOT=/app/staticfiles

# Copy virtual environment from builder
COPY --from=builder --chown=edumanage:edumanage /app/.venv /app/.venv

# Copy application source code
COPY --chown=edumanage:edumanage . .

# Setup entrypoint script and prepare staticfiles directory
RUN chmod +x /app/entrypoint.sh && \
    mkdir -p /app/staticfiles && \
    chown -R edumanage:edumanage /app

USER edumanage

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/health/ || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
