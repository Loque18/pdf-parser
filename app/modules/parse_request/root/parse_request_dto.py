from typing import TYPE_CHECKING

from pydantic import BaseModel, RootModel

from app.lib.storage.storage_service import StoredFile

if TYPE_CHECKING:
    from app.lib.alembic.parse_job_model import ParseJob
    from app.lib.alembic.parse_request_model import ParseRequest

class CreateRequestDto(BaseModel):
    storage_id: str
    stored_files: list[StoredFile]

class ListUserParsePetitionsRequest(BaseModel):
    anon_id: str


# ==================================================
# RESOURCES SCHEMAS
# ==================================================
class FileSummary(BaseModel):
    original_name: str
    url: str
    mime_type: str
    size: int

class OutputResult(BaseModel):
    id: str
    payload: dict


class JobSummary(BaseModel):
    id: str
    status: str
    created_at: str
    started_at: str | None
    finished_at: str | None
    error_message: str | None
    file: FileSummary
    output: OutputResult | None


# ==================================================
# RESPONSES
# ==================================================
class CreateParseRequestResponse(BaseModel):
    id: str
    status: str
    created_at: str
    expires_at: str | None

class RetrieveRequestResponse(BaseModel):
    id: str
    status: str
    created_at: str
    expires_at: str    
    jobs: list[JobSummary]

class ListUserParseRequestsResponse(RootModel[list[RetrieveRequestResponse]]):
    pass

# ==================================================
# RESPONSE BUILDERS
# ==================================================

class ResponseBuilder:
    @staticmethod
    def _build_job(job: "ParseJob") -> JobSummary:
        return JobSummary(
            id=job.id,
            status=job.status.value,
            created_at=job.created_at.isoformat(),
            started_at=job.started_at.isoformat() if job.started_at else None,
            finished_at=job.finished_at.isoformat() if job.finished_at else None,
            error_message=job.error_message,
            file=FileSummary(
                original_name=job.request_file.original_name,
                url=job.request_file.url,
                mime_type=job.request_file.mime_type,
                size=job.request_file.size,
            ),
            output=(
                None
                if job.parser_output is None
                else OutputResult(
                    id=str(job.parser_output.id),
                    payload=job.parser_output.payload,
                )
            ),
        )

    @classmethod
    def build_retrieve_request(
        cls,
        parse_request: "ParseRequest",
    ) -> RetrieveRequestResponse:
        return RetrieveRequestResponse(
            id=parse_request.id,
            status=parse_request.status.value,
            created_at=parse_request.created_at.isoformat(),
            expires_at=(
                parse_request.expires_at.isoformat()
                if parse_request.expires_at
                else ""
            ),
            jobs=[cls._build_job(job) for job in parse_request.request_jobs],
        )

    @classmethod
    def build_list_requests(
        cls,
        parse_requests: list["ParseRequest"],
    ) -> ListUserParseRequestsResponse:
        return ListUserParseRequestsResponse(
            [cls.build_retrieve_request(parse_request) for parse_request in parse_requests]
        )
