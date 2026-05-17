from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.lib.alembic.parser_output_model import ParserOutput
from app.modules.parse_request.output.output_dto import OutputDTO


class OutputRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_output(
        self,
        dto: OutputDTO,
    ) -> ParserOutput:
        parser_output = ParserOutput(
            parser_file_id=dto.parser_file_id,
            status=dto.status,
            payload=dto.payload,
            error_message=dto.error_message,
        )
        self.db.add(parser_output)
        self.db.commit()
        self.db.refresh(parser_output)
        return parser_output

    def get_output(self, output_id: int) -> ParserOutput | None:
        return self.db.get(ParserOutput, output_id)

    def get_by_parser_file_id(self, parser_file_id: str) -> ParserOutput | None:
        statement = select(ParserOutput).where(
            ParserOutput.parser_file_id == parser_file_id
        )
        return self.db.scalar(statement)

    def mark_processed(
        self,
        dto: OutputDTO,
    ) -> ParserOutput | None:
        parser_output = self.get_by_parser_file_id(dto.parser_file_id)
        if parser_output is None:
            return None

        parser_output.status = dto.status
        parser_output.payload = dto.payload
        parser_output.error_message = dto.error_message
        parser_output.processed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(parser_output)
        return parser_output

    def mark_failed(
        self,
        dto: OutputDTO,
    ) -> ParserOutput | None:
        parser_output = self.get_by_parser_file_id(dto.parser_file_id)
        if parser_output is None:
            return None

        parser_output.status = dto.status
        parser_output.payload = dto.payload
        parser_output.error_message = dto.error_message
        self.db.commit()
        self.db.refresh(parser_output)
        return parser_output
