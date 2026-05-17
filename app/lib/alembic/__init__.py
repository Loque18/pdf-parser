"""Central SQLAlchemy model registry for Alembic."""

from app.lib.alembic import (  # noqa: F401
    outbox_model,
    parse_job_model,
    parser_output_model,
    parse_request_model,
    request_file_model,
)
