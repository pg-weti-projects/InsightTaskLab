FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY backend/pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

COPY backend /app/backend

WORKDIR /app/backend

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
