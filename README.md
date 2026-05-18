# PDF Parser API

FastAPI service for uploading PDF files, creating parse requests, processing one job per file, and storing normalized outputs.

## Local development

Install dependencies with `uv`:

```bash
uv sync
```

Start the API:

```bash
uv run uvicorn main:app --reload
```

Start the worker:

```bash
uv run dramatiq app.modules.parse_request.jobs --processes 1 --threads 1
```

Run tests:

```bash
uv run pytest
```

## Migrations

Apply migrations:

```bash
uv run alembic upgrade head
```

Create a new migration:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

## Docker deployment

### 1. Create `.env`

Copy the example file:

```bash
cp .env.example .env
```

Fill the values before starting the stack.

### 2. Environment variables

The application reads these values from `.env`.

Application:

- `APP_NAME`: FastAPI application name shown in docs and metadata.
- `APP_VERSION`: application version shown in docs and metadata.

Database:

- `DATABASE_URL`: SQLAlchemy connection string used by the API and worker.
- `POSTGRES_DB`: database name for the Postgres container.
- `POSTGRES_USER`: database user for the Postgres container.
- `POSTGRES_PASSWORD`: database password for the Postgres container.

Queue:

- `REDIS_URL`: Redis connection string used by background jobs.

PDF extraction:

- `LLAMA_API_KEY`: API key used for Llama Cloud PDF parsing.

LLM:

- `LLM_API_KEY`: API key used by the LLM client.
- `LLM_MODEL`: model name used by the LLM client.

Observability:

- `LANGSMITH_API_KEY`: LangSmith API key.
- `LANGSMITH_TRACING`: enables or disables LangSmith tracing.
- `LANGSMITH_PROJECT`: LangSmith project name.

### 3. Start the stack

Build and run:

```bash
docker compose up --build
```

This starts:

- `api` on `http://localhost:8000`
- `worker` for Dramatiq jobs
- `db` on `localhost:5432`

The API container runs:

```bash
alembic upgrade head
```

before starting Uvicorn.

### 4. Stop the stack

```bash
docker compose down
```

To also remove the database volume:

```bash
docker compose down -v
```
