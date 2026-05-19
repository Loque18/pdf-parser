# API Design

## Resources

- `parse_request`: request-level metadata and aggregate state
- `request_file`: raw file reference to the storage provider
- `parse_job`: processing lifecycle per file
- `parse_output`: final parsed result for one job

## Main Endpoints

- `POST /parser`
- `GET /parser/requests`
- `GET /parser/requests/{request_id}`

## Authentication / Client Scope

The parse request endpoints are scoped by client identity using the HTTP header:

```text
X-client-Id: <anonId>
```

Used by:

- `POST /parser`
- `GET /parser/requests`
- `GET /parser/requests/{request_id}`

If the header is missing, the request should fail validation.

## POST /parser

Purpose:
- Accept a multipart upload with multiple files
- Create one `parse_request`
- Create one `request_file` per uploaded file
- Create one `parse_job` per uploaded file
- Enqueue one background job per file

Current response:

```json
{
  "id": "request-id",
  "status": "pending",
  "created_at": "2026-05-16T19:00:00Z",
  "expires_at": null
}
```

Current status code:
- `200 OK`

## GET /parser/requests

Purpose:
- List parse requests that belong to the client identified by `X-client-Id`
- Return one item per request
- Include jobs, file metadata, and outputs

Current response:

```json
[
  {
    "id": "request-id",
    "status": "processed",
    "created_at": "2026-05-16T19:00:00Z",
    "expires_at": "2026-05-17T19:00:00Z",
    "jobs": [
      {
        "id": "job-id",
        "status": "processed",
        "created_at": "2026-05-16T19:00:00Z",
        "started_at": "2026-05-16T19:01:00Z",
        "finished_at": "2026-05-16T19:01:05Z",
        "error_message": null,
        "file": {
          "original_name": "invoice.pdf",
          "url": "uploads/parse_requests/storage-id/invoice.pdf",
          "mime_type": "application/pdf",
          "size": 12345
        },
        "output": {
          "id": "1",
          "payload": {
            "tables": [
              {
                "header": ["invoice ID", "Customer"],
                "rows": [["inv1", "Acme Corp"]]
              }
            ]
          }
        }
      }
    ]
  }
]
```

## GET /parser/requests/{request_id}

Purpose:
- Retrieve one parse request scoped by `X-client-Id`
- Return its jobs, file metadata, and final outputs

Current response:

```json
{
  "id": "request-id",
  "status": "processing",
  "created_at": "2026-05-16T19:00:00Z",
  "expires_at": "2026-05-17T19:00:00Z",
  "jobs": [
    {
      "id": "job-id",
      "status": "processed",
      "created_at": "2026-05-16T19:00:00Z",
      "started_at": "2026-05-16T19:01:00Z",
      "finished_at": "2026-05-16T19:01:05Z",
      "error_message": null,
      "file": {
        "original_name": "invoice.pdf",
        "url": "uploads/parse_requests/storage-id/invoice.pdf",
        "mime_type": "application/pdf",
        "size": 12345
      },
      "output": {
        "id": "1",
        "payload": {
          "tables": [
            {
              "header": ["invoice ID", "Customer"],
              "rows": [["inv1", "Acme Corp"]]
            }
          ]
        }
      }
    }
  ]
}
```

## Static files

Uploaded files are served publicly through:

```text
GET /uploads/<path>
```

Example:

```text
/uploads/parse_requests/<storage_id>/invoice.pdf
```

## Status Model

### parse_request.status

- `pending`
- `processing`
- `processed`
- `failed`

### parse_job.status

- `pending`
- `processing`
- `processed`
- `failed`

## Response Shapes

### CreateParseRequestResponse

```json
{
  "id": "request-id",
  "status": "pending",
  "created_at": "2026-05-16T19:00:00Z",
  "expires_at": null
}
```

### RetrieveRequestResponse

```json
{
  "id": "request-id",
  "status": "processed",
  "created_at": "2026-05-16T19:00:00Z",
  "expires_at": "2026-05-17T19:00:00Z",
  "jobs": [
    {
      "id": "job-id",
      "status": "processed",
      "created_at": "2026-05-16T19:00:00Z",
      "started_at": "2026-05-16T19:01:00Z",
      "finished_at": "2026-05-16T19:01:05Z",
      "error_message": null,
      {
        "original_name": "invoice.pdf",
        "url": "uploads/parse_requests/storage-id/invoice.pdf",
        "mime_type": "application/pdf",
        "size": 12345
      },
      "output": {
        "id": "1",
        "payload": {
          "tables": [
            {
              "header": ["invoice ID", "Customer"],
              "rows": [["inv1", "Acme Corp"]]
            }
          ]
        }
      }
    ]
  ]
}
```

## Public vs Internal Resources

Public:
- `parse_request` via `/parser`
- uploaded assets via `/uploads`

Internal:
- `request_file`
- `parse_job`
- `parse_output`

These internal resources should not have standalone CRUD endpoints initially.

## Notes

- `parse_request` is the main aggregate returned to clients
- `request_file` is only a storage reference
- `parse_job` is the actual worker unit
- `parse_output` stores the parsed result payload
- ownership is scoped by `anon_id` persisted on `parse_request`
- `X-client-Id` is required to create, list, and retrieve requests
