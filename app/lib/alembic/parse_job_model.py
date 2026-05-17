from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.lib.db import Base

if TYPE_CHECKING:
    from app.lib.alembic.parse_request_model import ParseRequest
    from app.lib.alembic.request_file_model import RequestFile
    from app.lib.alembic.parser_output_model import ParserOutput


class ParseJobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    processed = "processed"
    failed = "failed"


class ParseJob(Base):
    __tablename__ = "parse_jobs"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4()),
    )


    status: Mapped[ParseJobStatus] = mapped_column(
        SqlEnum(ParseJobStatus, name="parse_job_status"),
        default=ParseJobStatus.pending,
        nullable=False,
    )

    error_message: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    request_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("parse_requests.id", ondelete="CASCADE"),
        nullable=False,        
    )
        
    request_file_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("request_files.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # ----- relationships ----- #
  

    parse_request: Mapped["ParseRequest"] = relationship(
        back_populates="request_jobs",
    )

    request_file: Mapped["RequestFile"] = relationship(
        back_populates="parse_job",
    )


    parser_output: Mapped["ParserOutput | None"] = relationship(
        back_populates="parse_job",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
