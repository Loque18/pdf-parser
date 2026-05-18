# FastAPI API

Initial scaffold for a FastAPI service.

## Structure

```text
.
|-- app/
|   |-- lib/
|   |   `-- config.py
|   |-- main.py
|   `-- modules/
|       `-- health/
|           |-- dtos.py
|           |-- router.py
|           `-- services.py
|-- tests/
|   `-- test_health.py
|-- main.py
`-- pyproject.toml
```

## Run

Install dependencies:

```bash
pip install -e .[dev]
```

Start the API:

```bash
uvicorn main:app --reload
```

Start a Dramatiq worker:

```bash
dramatiq app.lib.queue:redis_broker worker
```

## Endpoints

- `GET /health` returns service health metadata.

## Test

```bash
pytest
```

## Migrations

Create or apply database migrations with Alembic:

```bash
alembic upgrade head
alembic revision --autogenerate -m "describe change"
```

## Queue

Redis-backed jobs are configured with:

```env
REDIS_URL=redis://localhost:6379/0
JOB_QUEUE_ENABLED=true
```

Run the worker with:

```bash
dramatiq app.lib.queue:redis_broker worker
```

## Docker

Build and start the stack:

```bash
docker compose up --build
```

This starts:

- `api` on `http://localhost:8000`
- `worker` for Dramatiq jobs
- `db` on PostgreSQL `localhost:5432`
- `redis` on `localhost:6379`
