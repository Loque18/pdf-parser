import dramatiq

from app.lib import broker  # noqa: F401
from app.lib.di.db import get_session_factory
from app.modules.parser.parser_service import process_parser_job_by_id


@dramatiq.actor(queue_name="parser")
def process_parser_job(job_id: str) -> None:
    session = get_session_factory()()
    try:
        process_parser_job_by_id(session, job_id)
    finally:
        session.close()
