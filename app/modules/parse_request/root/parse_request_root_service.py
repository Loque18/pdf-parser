from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.lib.storage.storage_service import StorageService
from app.modules.parse_request.root.parse_request_root_repository import (
    ParseRequestRootRepository,
)

from app.modules.parse_request.jobs import process_parser_job

from app.modules.parse_request.root.parse_request_dto import (
    CreateRequestDto, 
    CreateParseRequestResponse,
    RetrieveRequestResponse,
    ListUserParseRequestsResponse,
)


async def parse_pdfs(
    db: Session,
    files: list[UploadFile],
    client_id: str,
) -> CreateParseRequestResponse:

    # 1. store files 
    storage_id = str(uuid4())
    storage_svc = StorageService()
    stored_files = await storage_svc.store_many(files, storage_key=f"parse_requests/{storage_id}")

    # 2. create parse request 
    repository = ParseRequestRootRepository(db)    
    dto = CreateRequestDto(
        storage_id=storage_id,
        stored_files=stored_files,
    )
    parse_request = repository.create_parse_request(dto, client_id)
    parse_request_with_jobs = repository.get_parse_request_with_jobs(parse_request.id)

    # 3. enqueue parser jobs
    for job in parse_request_with_jobs.request_jobs:
        process_parser_job.send(job.id)

    return CreateParseRequestResponse(
        id=parse_request.id,
        status=parse_request.status.value,
        created_at=parse_request.created_at.isoformat(),
        expires_at=(
            parse_request.expires_at.isoformat()
            if parse_request.expires_at
            else None
        ),
    )


def get_parse_request_by_id(
    db: Session,
    request_id: str,
    user_id: str,
) -> RetrieveRequestResponse:
    repository = ParseRequestRootRepository(db)
    parse_request = repository.retrieve_parse_request_by_id(request_id, user_id)

    if parse_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parse request not found",
        )

    return parse_request


def list_parse_requests_by_user_id(
    db: Session,
    user_id: str,
) -> ListUserParseRequestsResponse:
    repository = ParseRequestRootRepository(db)
    return repository.list_parse_requests_by_user_id(user_id)
