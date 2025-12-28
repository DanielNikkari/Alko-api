FROM python:3.13-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY . .

RUN uv sync --group mcp --locked --no-dev

CMD ["uv", "run", "python", "mcp/mcp_server.py"]
