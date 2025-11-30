# Stage 1: Builder - Install dependencies with uv
FROM ghcr.io/astral-sh/uv:python3.13-alpine AS builder

WORKDIR /app

# Set uv environment variables for optimization
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

# Install dependencies first (using bind mounts for better caching)
# This layer is cached unless uv.lock or pyproject.toml changes
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Copy the application code
COPY . /app

# Install the project itself (fast since dependencies are already installed)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Stage 2: Runtime - Minimal production image without uv
FROM python:3.13-alpine

WORKDIR /app

# Create non-root user for security
RUN addgroup -g 1001 -S nonroot && \
    adduser -u 1001 -S nonroot -G nonroot

# Copy the application and virtual environment from builder
COPY --from=builder --chown=nonroot:nonroot /app /app

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER nonroot

# Expose no ports - this MCP server uses stdio transport

# Health check is not applicable for stdio-based MCP servers
# as they don't expose HTTP endpoints

# Entry point for stdio communication with Claude Desktop
# The empty ENTRYPOINT disables uv's default entrypoint
ENTRYPOINT []
CMD ["python", "-m", "ns_bridge.server"]
