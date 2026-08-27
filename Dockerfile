# Builder stage
FROM python:3.10-slim AS builder

WORKDIR /app
COPY pyproject.toml .

RUN pip install --no-cache-dir pip==23.2.1 && \
    pip wheel --no-cache-dir --wheel-dir /app/wheels .

# Final stage
FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/pyproject.toml .

RUN pip install --no-cache /wheels/*

COPY ./src /app/src
COPY ./alembic /app/alembic
COPY ./alembic.ini /app/alembic.ini

ENV PYTHONPATH=/app/src

# Non-root runtime user -- mirrors the Node backend's Dockerfile
# (addgroup/adduser + USER before CMD), adapted to this image's Debian
# base (groupadd/useradd) rather than Alpine's syntax.
RUN groupadd --system app && useradd --system --gid app --no-create-home app
USER app

# Mirrors the Node backend's Dockerfile HEALTHCHECK (same
# interval/timeout/retries), hitting the same /health endpoint. Uses
# Python's own stdlib rather than installing curl, the same "no extra
# package just for the healthcheck" choice Node's one-liner makes.
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)" || exit 1

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
