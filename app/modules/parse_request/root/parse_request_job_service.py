import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.lib.ai.graphs.pdf_graph import build_pdf_graph
from app.lib.alembic.parse_job_model import ParseJob, ParseJobStatus
from app.lib.alembic.parse_request_model import ParseRequestStatus, ParseRequest
from app.lib.alembic.request_file_model import RequestFile
from app.modules.parse_request.output.output_dto import OutputDTO
from app.modules.parse_request.output.output_repository import OutputRepository


def process_parse_job(db: Session, parse_job_id: str) -> None:
    asyncio.run(_process_parse_job(db, parse_job_id))


async def _process_parse_job(db: Session, parse_job_id: str) -> None:

    # select the job with related request file and parse request
    statement = (
        select(ParseJob)
        .options(
            selectinload(ParseJob.request_file),
            selectinload(ParseJob.parse_request),
            selectinload(ParseJob.parser_output),
        )
        .where(ParseJob.id == parse_job_id)
    )
    parse_job = db.scalar(statement)
    print(parse_job)
    if parse_job is None:
        return

    request_file = parse_job.request_file
    parse_request = parse_job.parse_request

    # update job status to processing
    now = datetime.now(timezone.utc)
    parse_job.status = ParseJobStatus.processing
    parse_job.started_at = now
    parse_job.error_message = None
    if parse_request.status == ParseRequestStatus.pending:
        parse_request.status = ParseRequestStatus.processing
    db.commit()
    db.refresh(parse_job)

    output_repository = OutputRepository(db)

    try:
        # extract data from graph
        print("calling graph")
        graph = build_pdf_graph()
        result = await graph.ainvoke({"pdf_path": "storage/"+ request_file.storage_key})

        # create output
        output_dto = OutputDTO(
            parse_job_id=parse_job.id,
            status="processed",
            payload=result.get("normalized_data", []),
        )
        if output_repository.get_by_parse_job_id(parse_job.id) is None:
            output_repository.create_output(output_dto)
        else:
            output_repository.mark_processed(output_dto)

        # finalize job
        print("doing job")
        parse_job.status = ParseJobStatus.processed
        parse_job.finished_at = datetime.now(timezone.utc)
        parse_job.error_message = None
    except Exception as exc:
        failed_output = OutputDTO(
            parse_job_id=parse_job.id,
            status="failed",
            error_message=str(exc),
        )
        if output_repository.get_by_parse_job_id(parse_job.id) is None:
            output_repository.create_output(failed_output)
        else:
            output_repository.mark_failed(failed_output)

        parse_job.status = ParseJobStatus.failed
        parse_job.error_message = str(exc)
        parse_job.finished_at = datetime.now(timezone.utc)
        _sync_parse_request_status(parse_request)
        db.commit()
        raise

    _sync_parse_request_status(parse_request)
    db.commit()


def _sync_parse_request_status(parse_request: ParseRequest) -> None:
    jobs = [job for job in parse_request.request_jobs if job is not None]        
    if not jobs:
        parse_request.status = ParseRequestStatus.pending
        return

    statuses = {job.status for job in jobs}
    if any(status == ParseJobStatus.processing for status in statuses):
        parse_request.status = ParseRequestStatus.processing
    elif all(status == ParseJobStatus.processed for status in statuses):
        parse_request.status = ParseRequestStatus.processed
        parse_request.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    elif all(status == ParseJobStatus.failed for status in statuses):
        parse_request.status = ParseRequestStatus.failed
        parse_request.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    else:
        parse_request.status = ParseRequestStatus.processing
