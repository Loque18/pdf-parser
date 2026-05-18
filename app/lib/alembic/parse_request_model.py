from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, Enum as SqlEnum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.lib.db import Base

if TYPE_CHECKING:
    from app.lib.alembic.request_file_model import RequestFile
    from app.lib.alembic.parse_job_model import ParseJob


class ParseRequestStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    processed = "processed"
    failed = "failed"


class ParseRequest(Base):
    __tablename__ = "parse_requests"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    storage_id: Mapped[str] = mapped_column(
        String,
        default=lambda: str(uuid4()),
        nullable=False,
    )
    status: Mapped[ParseRequestStatus] = mapped_column(
        SqlEnum(ParseRequestStatus, name="parse_request_status"),
        default=ParseRequestStatus.pending,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    anon_id: Mapped[str | None] = mapped_column(String, nullable=True)
    # ----- relationships ----- #

    request_files: Mapped[list["RequestFile"]] = relationship(        
        "RequestFile",
        back_populates="parse_request",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    request_jobs: Mapped[list["ParseJob"]] = relationship(        
        "ParseJob",
        back_populates="parse_request",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
