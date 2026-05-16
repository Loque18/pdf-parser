from sqlalchemy.orm import Mapped, mapped_column

from app.lib.db import Base


class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(primary_key=True)
