<!-- HEADER -->
<div align="center">
    <a href="https://www.alko.fi">
        <img src="/assets/alko-logo.svg" width="150px">
    </a>
    <h1>
        API
    </h1>
</div>

Alko product API implemented on ⚡ FastAPI.

<!-- SETUP -->
## Setting up data

**Sync**
```bash
uv sync
```
or
```bash
make install
```

**Get product data**
```bash
uv run python -m scraper.fetch_products
```
or
```bash
make fetch
```

<!-- API -->
## Running API

**Run server**
```bash
uv run fastapi run ./app/main.py
```

### Running in Container

**Sync**
```bash
uv sync
```

**Build**
```bash
docker build -f app/Dockerfile -t alko-api .
```
or
```bash
make build
```

**Run**
```bash
docker run --name alko-api --env ".env" -p "8080:80" alko-api
```
or
```bash
make run
```

**Clean up**
```bash
docker rm -f alko-api
```
or
```bash
make stop
```

## Health check

If everything is working as it should, the health check (`/health`) should look something like this:

<div align="center">
    <a href="#">
        <img src="/assets/health-check.png" width="250px" alt="health check example" >
    </a>
</div>

## API Documentation

Documentation is handled automatically by FastAPI and is available on endpoint `/docs`.

<!-- MCP -->
## Running MCP Server

You can serve the Alko product API to a LLM Client, for example, Claude desktop by adding the following to `claude_desktop_config.json`

```json
{
    "mcpServers": {
    "alko-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/Alko-api",
        "run",
        "mcp/mcp_server.py"
      ]
    }
  }
}
```
> [!NOTE]
> Remember to have your Alko API running for the MCP client!
