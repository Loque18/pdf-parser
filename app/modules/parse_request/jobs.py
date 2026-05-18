import dramatiq

from app.lib import broker  # noqa: F401
from app.lib.di.db import get_session_factory
from app.modules.parse_request.root.parse_request_job_service import (
    process_parse_job,
)


@dramatiq.actor(
    queue_name="parser",
    max_retries=5,
    min_backoff=10_000,  # 10 seconds
    max_backoff=300_000,  # 5 minutes
)
def process_parser_job(parse_job_id: str) -> None:
    session = get_session_factory()()
    try:
        process_parse_job(session, parse_job_id)
    finally:
        session.close()
