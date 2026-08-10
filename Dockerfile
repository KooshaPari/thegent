# syntax=docker/dockerfile:1.7
# thegent production image — multi-stage build for the Python 3.13 runtime.
#
# Stage 1: builder — install build deps and the full editable install into a
#   throwaway layer so the runtime image only carries the wheelhouse + site-packages.
# Stage 2: runtime — slim Python 3.13 base, non-root user, healthcheck.
#
# Usage:
#   docker build -t thegent:dev .
#   docker run --rm -it thegent:dev thegent --help
#
# The MCP HTTP server is exposed on port 8765 by default — see compose.yaml.

ARG PYTHON_VERSION=3.13
ARG UV_VERSION=0.5

# ---------------------------------------------------------------------------
# Stage 1: builder
# ---------------------------------------------------------------------------
FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS builder

ARG PYTHON_VERSION

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/thegent \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOAD_PRETTY=0

WORKDIR /build

# Copy ONLY the dependency files first so Docker can cache the wheelhouse
# layer when source changes don't touch dependencies.
COPY pyproject.toml uv.lock ./

# `--no-install-project` skips the package itself; we add it in a later layer
# so a source-only change doesn't bust the dependency cache.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Now copy the source tree and install the project itself.
COPY src ./src
COPY README.md ./README.md 2>/dev/null || true

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable


# ---------------------------------------------------------------------------
# Stage 2: runtime
# ---------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS runtime

LABEL org.opencontainers.image.title="thegent" \
      org.opencontainers.image.description="Unified agent orchestration CLI" \
      org.opencontainers.image.source="https://github.com/kooshapari/thegent" \
      org.opencontainers.image.licenses="MIT"

# Non-root user for the runtime — UID/GID 10001 to avoid collision with
# host users when bind-mounting volumes.
RUN groupadd --system --gid 10001 thegent \
    && useradd --system --uid 10001 --gid thegent --home /home/thegent --shell /usr/sbin/nologin thegent \
    && mkdir -p /home/thegent /app \
    && chown -R thegent:thegent /home/thegent /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PATH="/opt/thegent/bin:${PATH}" \
    THEGENT_HOME=/home/thegent/.thegent

# Copy the prebuilt venv from the builder stage. The venv is at /opt/thegent
# per UV_PROJECT_ENVIRONMENT above.
COPY --from=builder --chown=thegent:thegent /opt/thegent /opt/thegent
COPY --from=builder --chown=thegent:thegent /build/src /app/src

WORKDIR /app

USER thegent

# MCP HTTP default port (matches compose.yaml).
EXPOSE 8765

# Healthcheck probes the FastMCP `/health` endpoint. Curl is bundled in the
# slim image; if it's missing on a future base, swap to `python -c`.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail --silent http://localhost:8765/health || exit 1

# Default command — prints the CLI banner. Override with the MCP HTTP server
# in compose.yaml (`docker compose run thegent thegent mcp-http`).
CMD ["thegent", "--help"]