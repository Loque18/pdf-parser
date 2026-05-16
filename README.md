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
