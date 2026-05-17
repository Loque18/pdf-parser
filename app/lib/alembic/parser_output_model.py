from __future__ import annotations

from datetime import datetime
from typing import Any
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.lib.db import Base

if TYPE_CHECKING:
    from app.lib.alembic.parse_job_model import ParseJob


class ParserOutput(Base):
    __tablename__ = "parser_outputs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    parse_job_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("parse_jobs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # ----- relationships ----- #
  
    parse_job: Mapped["ParseJob"] = relationship(
        back_populates="parser_output",
    )
