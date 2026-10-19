# Development image for the Django backend. Not intended for production.

FROM ghcr.io/astral-sh/uv:0.11.28-python3.12-trixie-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install dependencies in a layer that survives source changes. The virtual
# environment stays outside /app so the development bind mount does not hide it.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .

EXPOSE 8000

# Apply migrations on startup and run Django's autoreloading development server.
CMD ["sh", "-c", "uv run --no-sync manage.py migrate && uv run --no-sync manage.py runserver 0.0.0.0:8000"]
