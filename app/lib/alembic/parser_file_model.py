from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.lib.db import Base

if TYPE_CHECKING:
    from app.lib.alembic.parse_request_model import ParseRequest


class ParserFile(Base):
    __tablename__ = "parser_files"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    key: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    parse_request_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("parse_requests.id", ondelete="CASCADE"),
        nullable=False,
    )
    size: Mapped[int] = mapped_column(nullable=False)

    parse_request: Mapped["ParseRequest"] = relationship(
        back_populates="parser_files",
    )
