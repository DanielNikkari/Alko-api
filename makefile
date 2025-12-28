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

# Open docs
docs:
	open http://127.0.0.1:8080/docs

# View logs
logs:
	docker logs -f alko-api

# Install dependencies
install:
	uv sync

# Run Alko MCP server directly
mcp-server:
	uv run mcp/mcp_server.py

### END-TO-END builds ###

# API
api:
	docker build -f app/Dockerfile -t alko-api .
	docker run -d --name alko-api --env-file .env -p 8080:80 alko-api

# MCP
mcp: api
	docker build -f mcp/Dockerfile -t alko-mcp .
	docker run -d --name alko-mcp-server --env-file .env -p 8081:80 alko-mcp

# Stop and remove container
stop:
	docker rm -f alko-api alko-mcp-server 2>/dev/null || true
