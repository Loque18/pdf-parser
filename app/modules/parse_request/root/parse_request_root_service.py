from typing import Any
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.lib.config import settings
from app.lib.storage.storage_service import StorageService
from app.modules.parse_request.root.parse_request_root_repository import (
    ParseRequestRootRepository,
)


async def parse_pdfs(db: Session, files: list[UploadFile]) -> dict[str, Any]:
    storage_id = str(uuid4())
    storage_svc = StorageService()
    stored_files = await storage_svc.store_many(files, key=f"parse_requests/{storage_id}")

    repository = ParseRequestRootRepository(db)
    parse_request = repository.create_parse_request(storage_id, stored_files)

    if settings.job_queue_enabled:
        from app.modules.parse_request.jobs import process_parser_job

        process_parser_job.send(parse_request.id)

    return {        
        "request_id": parse_request.id
    }


def get_parse_request_by_id(db: Session, request_id: str) -> dict[str, Any]:
    repository = ParseRequestRootRepository(db)
    parse_request = repository.get_parse_request_with_files(request_id)

    if parse_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parse request not found",
        )

    results: list[dict[str, Any]] | None = None
    if parse_request.status.value != "pending":
        results = []
        for parser_file in parse_request.parser_files:
            results.append(
                {
                    "file": {
                        "original_name": parser_file.original_name,
                        "url": parser_file.url,
                        "key": parser_file.key,
                    },
                    "output": (
                        None
                        if parser_file.parser_output is None
                        else {
                            "id": parser_file.parser_output.id,
                            "payload": parser_file.parser_output.payload,
                        }
                    ),
                }
            )

    return {
        "parse_req": {
            "id": parse_request.id,
            "status": parse_request.status.value,
            "created_at": parse_request.created_at.isoformat(),
            "started_at": (
                parse_request.started_at.isoformat()
                if parse_request.started_at
                else None
            ),
            "finished_at": (
                parse_request.finished_at.isoformat()
                if parse_request.finished_at
                else None
            ),
            "error_message": parse_request.error_message,
            "results": results,
        }
    }
