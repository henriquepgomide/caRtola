ARG PYTHON_VERSION=3.12
ARG DEBIAN_RELEASE=bookworm

# ---------- builder ----------
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-${DEBIAN_RELEASE}-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# Install dependencies first (cacheable layer keyed on lockfile + manifest).
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Install the project itself.
COPY src ./src
COPY conf ./conf
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ---------- runtime ----------
FROM python:${PYTHON_VERSION}-slim-${DEBIAN_RELEASE} AS runtime

ARG KEDRO_UID=999
ARG KEDRO_GID=0

ENV PATH=/app/.venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN groupadd -f -g ${KEDRO_GID} kedro_group && \
    useradd -d /home/kedro -s /bin/bash -g ${KEDRO_GID} -u ${KEDRO_UID} kedro && \
    mkdir -p /app && chown -R kedro:${KEDRO_GID} /app

WORKDIR /app

COPY --from=builder --chown=kedro:${KEDRO_GID} /app/.venv /app/.venv
COPY --from=builder --chown=kedro:${KEDRO_GID} /app/src /app/src
COPY --from=builder --chown=kedro:${KEDRO_GID} /app/conf /app/conf

USER kedro

# kedro-viz default port (only used when running `kedro viz`).
EXPOSE 4141

CMD ["kedro", "run"]
