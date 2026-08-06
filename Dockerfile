# Builder stage
FROM python:3.10-slim as builder

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

ENV PYTHONPATH=/app/src

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
