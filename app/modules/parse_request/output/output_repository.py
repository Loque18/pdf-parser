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
            parse_job_id=dto.parse_job_id,
            payload=dto.payload or {},
        )
        self.db.add(parser_output)
        self.db.commit()
        self.db.refresh(parser_output)
        return parser_output

    def get_output(self, output_id: int) -> ParserOutput | None:
        return self.db.get(ParserOutput, output_id)

    def get_by_parse_job_id(self, parse_job_id: str) -> ParserOutput | None:
        statement = select(ParserOutput).where(
            ParserOutput.parse_job_id == parse_job_id
        )
        return self.db.scalar(statement)

    def mark_processed(
        self,
        dto: OutputDTO,
    ) -> ParserOutput | None:
        parser_output = self.get_by_parse_job_id(dto.parse_job_id)
        if parser_output is None:
            return None

        parser_output.payload = dto.payload or {}
        self.db.commit()
        self.db.refresh(parser_output)
        return parser_output

    def mark_failed(
        self,
        dto: OutputDTO,
    ) -> ParserOutput | None:
        parser_output = self.get_by_parse_job_id(dto.parse_job_id)
        if parser_output is None:
            return None

        parser_output.payload = dto.payload or {}
        self.db.commit()
        self.db.refresh(parser_output)
        return parser_output
