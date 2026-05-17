# API Design

## Resources

- `parse_request`: request-level metadata and aggregate state
- `request_file`: raw file reference to the storage provider
- `parse_job`: processing lifecycle per file
- `parse_output`: final parsed result for one job

## Main Endpoints

- `POST /parse-requests`
- `GET /parse-requests/{request_id}`

## POST /parse-requests

Purpose:
- Accept a multipart upload with multiple files
- Create one `parse_request`
- Create one `request_file` per uploaded file
- Create one `parse_job` per uploaded file
- Enqueue one background job per file

Suggested response:

```json
{
  "parse_request": {
    "id": "request-id",
    "status": "pending",
    "created_at": "2026-05-16T19:00:00Z"
  }
}
```

Recommended status code:
- `202 Accepted`

## GET /parse-requests/{request_id}

Purpose:
- Poll the aggregate request status
- Return per-file processing state and final output

Suggested response:

```json
{
  "parse_request": {
    "id": "request-id",
    "status": "processing",
    "created_at": "2026-05-16T19:00:00Z",
    "expires_at": "2026-05-17T19:00:00Z",
    "results": [
      {
        "file": {
          "id": "file-id",
          "original_name": "invoice.pdf",
          "url": "storage/parse_requests/storage-id/invoice.pdf",
          "key": "parse_requests/storage-id/invoice.pdf"
        },
        "job": {
          "id": "job-id",
          "status": "processed",
          "created_at": "2026-05-16T19:00:00Z",
          "started_at": "2026-05-16T19:01:00Z",
          "finished_at": "2026-05-16T19:01:05Z",
          "error_message": null
        },
        "output": {
          "id": 1,
          "payload": [
            {
              "customer": "ACME Corp",
              "amount": 100.0,
              "tax_rate": 19,
              "tax_amount": 19.0,
              "total": 119.0
            }
          ]
        }
      }
    ]
  }
}
```

If the request is still pending:
- `results` may be `null`

## Status Model

### parse_request.status

- `pending`
- `processing`
- `processed`
- `failed`
- optional later: `partial`

### parse_job.status

- `pending`
- `processing`
- `processed`
- `failed`

## Public vs Internal Resources

Public:
- `parse_request`

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
