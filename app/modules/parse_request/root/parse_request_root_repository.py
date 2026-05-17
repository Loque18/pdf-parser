from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.lib.alembic.parse_request_model import ParseRequest, ParseRequestStatus
from app.lib.alembic.parser_file_model import ParserFile
from app.lib.storage.storage_service import StoredFile


class ParseRequestRootRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_parse_request(
        self,
        storage_id: str,
        stored_files: list[StoredFile],
    ) -> ParseRequest:
        parse_request = ParseRequest(
            id=str(uuid4()),
            storage_id=storage_id,
            status=ParseRequestStatus.pending,
        )
        self.db.add(parse_request)
        self.db.flush()

        for stored_file in stored_files:
            self.db.add(
                ParserFile(
                    original_name=stored_file.original_name,
                    key=stored_file.key or "",
                    url=stored_file.stored_path,
                    parse_request_id=parse_request.id,
                    size=stored_file.size,
                )
            )

        self.db.commit()
        self.db.refresh(parse_request)
        return parse_request

    def get_parse_request(self, request_id: str) -> ParseRequest | None:
        return self.db.get(ParseRequest, request_id)

    def get_parse_request_with_files(self, request_id: str) -> ParseRequest | None:
        statement = (
            select(ParseRequest)
            .options(
                selectinload(ParseRequest.parser_files).selectinload(
                    ParserFile.parser_output
                )
            )
            .where(ParseRequest.id == request_id)
        )
        return self.db.scalar(statement)

    def mark_processing(self, request_id: str) -> ParseRequest | None:
        parse_request = self.get_parse_request(request_id)
        if parse_request is None:
            return None

        parse_request.status = ParseRequestStatus.processing
        parse_request.started_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(parse_request)
        return parse_request

    def mark_processed(self, request_id: str) -> ParseRequest | None:
        parse_request = self.get_parse_request(request_id)
        if parse_request is None:
            return None

        now = datetime.now(timezone.utc)
        parse_request.status = ParseRequestStatus.processed
        parse_request.finished_at = now
        parse_request.expires_at = now + timedelta(hours=24)
        self.db.commit()
        self.db.refresh(parse_request)
        return parse_request

    def mark_failed(self, request_id: str, error_message: str) -> ParseRequest | None:
        parse_request = self.get_parse_request(request_id)
        if parse_request is None:
            return None

        now = datetime.now(timezone.utc)
        parse_request.status = ParseRequestStatus.failed
        parse_request.error_message = error_message
        parse_request.finished_at = now
        parse_request.expires_at = now + timedelta(hours=24)
        self.db.commit()
        self.db.refresh(parse_request)
        return parse_request
