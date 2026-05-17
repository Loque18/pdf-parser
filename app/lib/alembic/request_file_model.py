from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.lib.db import Base

if TYPE_CHECKING:
    from app.lib.alembic.parse_job_model import ParseJob
    from app.lib.alembic.parse_request_model import ParseRequest


class RequestFile(Base):
    __tablename__ = "request_files"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    original_name: Mapped[str] = mapped_column(String, nullable=False)
    mime_type: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[int] = mapped_column(nullable=False)
    storage_key: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)    
    

    parse_request_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("parse_requests.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ----- relationships ----- #

    parse_request: Mapped["ParseRequest"] = relationship(        
        back_populates="request_files",
    )


    # parse_job: Mapped["ParseJob | None"] = relationship(
    #     back_populates="request_file",
    #     cascade="all, delete-orphan",
    #     passive_deletes=True,
    #     uselist=False,
    # )
