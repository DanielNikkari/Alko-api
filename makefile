.PHONY: dev fetch build run stop docs logs install mcp

# Run locally
dev:
	uv run fastapi dev app/main.py

# Fetch product data
fetch:
	uv run python -m scraper.fetch_products

# Build Docker image
build:
	docker build -f app/Dockerfile -t alko-api .

# Run Docker container
run:
	docker run --name alko-api --env-file .env -p 8080:80 alko-api

# Stop and remove container
stop:
	docker rm -f alko-api

# Open docs
docs:
	open http://127.0.0.1:8080/docs

# View logs
logs:
	docker logs -f alko-api

# Install dependencies
install:
	uv sync

# Run Alko MCP server
mcp:
	uv run mcp/mcp_server.py
