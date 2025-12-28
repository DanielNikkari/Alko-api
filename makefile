.PHONY: help install dev fetch stop logs docs \
        build-api build-mcp build \
        run-api run-mcp run \
        restart

.DEFAULT_GOAL := help

# ============================================================================
# Help
# ============================================================================

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Development:"
	@echo "  install     Install dependencies"
	@echo "  dev         Run API locally with hot reload"
	@echo "  fetch       Fetch product data from Alko"
	@echo "  mcp-dev     Run MCP server locally"
	@echo ""
	@echo "Docker:"
	@echo "  build       Build all images"
	@echo "  run         Build and run all containers"
	@echo "  stop        Stop and remove all containers"
	@echo "  restart     Restart all containers"
	@echo "  logs        Follow API container logs"
	@echo ""
	@echo "Utilities:"
	@echo "  docs        Open API docs in browser"

# ============================================================================
# Development
# ============================================================================

install:
	uv sync --all-groups

dev: install
	uv run fastapi dev app/main.py --reload

fetch:
	uv run python -m scraper.fetch_products

mcp-dev:
	uv run mcp/mcp_server.py

# ============================================================================
# Docker - Build
# ============================================================================

build-api:
	docker build -f app/Dockerfile -t alko-api .

build-mcp:
	docker build -f mcp/Dockerfile -t alko-mcp .

build: build-api build-mcp

# ============================================================================
# Docker - Run
# ============================================================================

run-api: build-api
	docker run -d --name alko-api --env-file .env -p 8080:80 alko-api

run-mcp: run-api build-mcp
	docker run -d --name alko-mcp-server --env-file .env -p 8081:80 alko-mcp

run: run-mcp

stop:
	@docker rm -f alko-api alko-mcp-server 2>/dev/null || true

restart: stop run

logs:
	docker logs -f alko-api

# ============================================================================
# Utilities
# ============================================================================

docs:
	open http://127.0.0.1:8080/docs
