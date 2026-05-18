# Architecture C4

## System Context

```mermaid
C4Context
    title PDF Parser - System Context

    Person(client, "Client Application", "Uploads PDFs and polls parse requests using X-client-Id")

    System(api, "PDF Parser API", "FastAPI service for request intake, file serving, and result retrieval")
    System_Ext(openai, "OpenAI", "LLM used to normalize extracted document data")
    System_Ext(llama, "Llama Cloud", "PDF parsing and text extraction service")
    System_Ext(redis, "Redis", "External background job queue")

    Rel(client, api, "POST /parser, GET /parser/requests, GET /parser/requests/{id}", "HTTPS + X-client-Id")
    Rel(client, api, "Downloads uploaded files", "GET /uploads/*")
    Rel(api, redis, "Enqueues parse_job ids", "Redis")
    Rel(api, llama, "Extracts PDF text", "HTTPS")
    Rel(api, openai, "Normalizes extracted content", "HTTPS")
```

## Container View

```mermaid
C4Container
    title PDF Parser - Container View

    Person(client, "Client Application", "Uploads PDFs, polls parse requests, and retrieves uploaded files")

    System_Boundary(pdf_parser, "PDF Parser") {
        Container(api, "API", "FastAPI + Uvicorn", "Receives PDFs, stores files, creates parse requests/jobs, serves /uploads, exposes results scoped by X-client-Id")
        Container(worker, "Worker", "Dramatiq", "Processes one parse job per file")
        ContainerDb(db, "PostgreSQL", "PostgreSQL", "Stores parse_request, request_file, parse_job, parse_output")
        Container(storage, "Local Storage", "Filesystem", "Stores uploaded PDF files under parse_requests/<storage_id>/")
    }

    System_Ext(openai, "OpenAI", "LLM normalization service")
    System_Ext(llama, "Llama Cloud", "PDF parsing/text extraction service")
    System_Ext(redis, "Redis", "External background job queue")

    Rel(client, api, "POST /parser", "HTTPS + X-client-Id")
    Rel(client, api, "GET /parser/requests", "HTTPS + X-client-Id")
    Rel(client, api, "GET /parser/requests/{request_id}", "HTTPS + X-client-Id")
    Rel(client, storage, "Downloads uploaded files", "GET /uploads/* via API static mount")
    Rel(api, storage, "Stores uploaded files", "Filesystem")
    Rel(api, db, "Creates requests/files/jobs and reads status", "SQL")
    Rel(api, redis, "Enqueues parse_job ids", "Redis")

    Rel(worker, redis, "Consumes parse jobs", "Redis")
    Rel(worker, db, "Updates jobs and outputs", "SQL")
    Rel(worker, storage, "Reads stored PDFs", "Filesystem")
    Rel(worker, llama, "Extracts raw text", "HTTPS")
    Rel(worker, openai, "Builds normalized JSON output", "HTTPS")
```

## Notes

- `parse_request` is scoped by `anon_id`, passed through the `X-client-Id` header.
- Uploaded files are stored on disk and served publicly through `/uploads`.
- `parse_request` creates one `request_file` and one `parse_job` per uploaded file.
- The worker processes one `parse_job` at a time and persists the final `parse_output`.
- PostgreSQL is part of the local Docker stack; Redis is currently expected as an external service via `REDIS_URL`.
