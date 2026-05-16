from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.lib.config import settings
from app.modules.parser.parser_repository import ParserRepository


async def parse_pdfs(db: Session, files: list[UploadFile]) -> dict[str, str]:
    _ = files

    repository = ParserRepository(db)
    job = repository.create_job()

    if settings.job_queue_enabled:
        from app.modules.parser.jobs import process_parser_job

        process_parser_job.send(job.id)

    return {
        "message": "ok",
        "job_id": job.id,
        "status": job.status.value,
    }


def process_parser_job_by_id(db: Session, job_id: str) -> None:
    repository = ParserRepository(db)
    job = repository.mark_running(job_id)

    if job is None:
        return

    try:
        print("doing job, saved pdf data to s3, updating job status to completed")
        repository.mark_completed(job_id)
    except Exception as exc:
        repository.mark_failed(job_id, str(exc))
        raise
