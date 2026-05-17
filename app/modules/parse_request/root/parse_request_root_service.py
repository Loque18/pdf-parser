import json
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.lib.config import settings
from app.lib.storage.storage_service import StorageService
from app.modules.parse_request.root.parse_request_root_repository import (
    ParseRequestRootRepository,
)

from app.modules.parse_request.jobs import process_parser_job

from app.modules.parse_request.root.parse_request_dto import CreateRequestDto



async def parse_pdfs(db: Session, files: list[UploadFile]) -> dict[str, Any]:
    storage_id = str(uuid4())
    storage_svc = StorageService()
    stored_files = await storage_svc.store_many(files, storage_key=f"parse_requests/{storage_id}")

    repository = ParseRequestRootRepository(db)    
    dto = CreateRequestDto(
        storage_id=storage_id,
        stored_files=stored_files,
    )
    parse_request = repository.create_parse_request(dto)
    parse_request_with_jobs = repository.get_parse_request_with_jobs(parse_request.id)


    for job in parse_request_with_jobs.request_jobs:
        process_parser_job.send(job.id)

    return {
        "id": parse_request.id,
        "status": parse_request.status.value,
        "created_at": parse_request.created_at.isoformat(),
        "expires_at": (
            parse_request.expires_at.isoformat()
            if parse_request.expires_at
            else None
        ),
    }


def get_parse_request_by_id(db: Session, request_id: str) -> dict[str, Any]:
    repository = ParseRequestRootRepository(db)
    parse_request = repository.get_parse_request_with_jobs(request_id)

    if parse_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parse request not found",
        )

    results: list[dict[str, Any]] | None = None
    if parse_request.status.value != "pending":
        results = []
        for request_file in parse_request.request_files:
            parser_output = None
            if request_file.parse_job is not None:
                parser_output = request_file.parse_job.parser_output

            results.append(
                {
                    "file": {
                        "original_name": request_file.original_name,
                        "url": request_file.url,
                        "key": request_file.storage_key,
                    },
                    "output": (
                        None
                        if parser_output is None
                        else {
                            "id": parser_output.id,
                            "payload": parser_output.payload,
                        }
                    ),
                }
            )

    return {
        "parse_req": {
            "id": parse_request.id,
            "status": parse_request.status.value,
            "created_at": parse_request.created_at.isoformat(),
            "started_at": None,
            "finished_at": None,
            "error_message": None,
            "results": results,
        }
    }
