from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.lib.alembic.parse_job_model import ParseJob, ParseJobStatus
from app.lib.alembic.parse_request_model import ParseRequest, ParseRequestStatus
from app.lib.alembic.request_file_model import RequestFile
from app.lib.storage.storage_service import StoredFile

# self
from app.modules.parse_request.root.parse_request_dto import (CreateRequestDto)


class ParseRequestRootRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_parse_request(
        self,
        dto: CreateRequestDto        
    ) -> ParseRequest:
        parse_request = ParseRequest(
            storage_id=dto.storage_id,
            status=ParseRequestStatus.pending,
        )
        self.db.add(parse_request)
        self.db.flush()

        for stored_file in dto.stored_files:
            request_file = RequestFile(
                original_name=stored_file.original_name,
                storage_key=stored_file.storage_key,
                mime_type=stored_file.mime_type,                
                url=stored_file.stored_path,
                parse_request_id=parse_request.id,
                size=stored_file.size,
            )
            self.db.add(request_file)
            self.db.flush()

            self.db.add(
                ParseJob(
                    request_id=parse_request.id,
                    request_file_id=request_file.id,
                    status=ParseJobStatus.pending,
                )
            )

        self.db.commit()
        self.db.refresh(parse_request)
        return parse_request

    def get_parse_request(self, request_id: str) -> ParseRequest | None:
        return self.db.get(ParseRequest, request_id)

    def get_parse_request_with_jobs(self, request_id: str) -> ParseRequest | None:
        statement = (
            select(ParseRequest)
            .options(                
                selectinload(ParseRequest.request_jobs)
            )
            .where(ParseRequest.id == request_id)
        )
        return self.db.scalar(statement)

    def mark_processing(self, request_id: str) -> ParseRequest | None:
        parse_request = self.get_parse_request(request_id)
        if parse_request is None:
            return None

        parse_request.status = ParseRequestStatus.processing
        self.db.commit()
        self.db.refresh(parse_request)
        return parse_request

    def mark_processed(self, request_id: str) -> ParseRequest | None:
        parse_request = self.get_parse_request(request_id)
        if parse_request is None:
            return None

        parse_request.status = ParseRequestStatus.processed
        parse_request.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        self.db.commit()
        self.db.refresh(parse_request)
        return parse_request

    def mark_failed(self, request_id: str, error_message: str) -> ParseRequest | None:
        parse_request = self.get_parse_request(request_id)
        if parse_request is None:
            return None

        parse_request.status = ParseRequestStatus.failed
        parse_request.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        self.db.commit()
        self.db.refresh(parse_request)
        return parse_request
