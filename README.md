<!-- HEADER -->
<div align="center">
    <a href="https://www.alko.fi">
        <img src="/assets/alko-logo.svg" width="150px">
    </a>
    <h1>
        API
    </h1>
</div>

Alko product API implemented on FastAPI ⚡.

## Setting up data

**Sync**
```bash
uv sync
```

**Get product data**
```bash
uv run python -m scraper.fetch_products
```

## Running API

**Run server**
```bash
uv run fastapi run ./app/main.py
```

### Running in Container 🐳

**Sync**
```bash
uv sync
```

**Build**
```bash
docker build -t alko-api .
```

**Run**
```bash
docker run --name alko-api --env ".env" -p "8080:80" alko-api
```

## Health check

If everything is working as it should, the health check (`/health`) should look something like this:

![health check example](/assets/health-check.png)

## API Documentation

Documentation is handled automatically by FastAPI and is available on endpoint `/docs`.
