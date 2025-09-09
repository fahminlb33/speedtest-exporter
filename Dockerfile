# ----- Build stage
FROM python:3.13-bookworm AS builder

ARG SPEEDTEST_VERSION=1.2.0
RUN --mount=type=cache,target=/tmp \
    ARCHITECTURE=$(uname -m) && \
    export ARCHITECTURE && \
    if [ "$ARCHITECTURE" = 'armv7l' ];then ARCHITECTURE="armhf";fi && \
    wget -nv -O /tmp/speedtest.tgz "https://install.speedtest.net/app/cli/ookla-speedtest-${SPEEDTEST_VERSION}-linux-${ARCHITECTURE}.tgz" && \
    tar zxvf /tmp/speedtest.tgz -C /tmp && \
    cp /tmp/speedtest /bin/speedtest

COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev

# ----- Production stage
FROM python:3.13-slim-bookworm AS production

ENV PATH="/app/.venv/bin:$PATH"
ENV SPEEDTEST_TIMEOUT=90
ENV SPEEDTEST_SERVER_ID=

WORKDIR /app

COPY --from=builder --chown=app:app /app /app
COPY --from=builder /bin/speedtest /bin/speedtest

EXPOSE 9898

CMD ["gunicorn", "--workers", "1", "--timeout", "300", "--bind", "0.0.0.0:9898", "main:app"]

HEALTHCHECK --timeout=10s CMD wget --no-verbose --tries=1 --spider http://localhost:9898/health
