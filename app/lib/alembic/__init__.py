"""Central SQLAlchemy model registry for Alembic."""

from app.lib.alembic import (  # noqa: F401
    entry_model,
    job_model,
    outbox_model,
    parse_request_model,
    parser_file_model,
)
