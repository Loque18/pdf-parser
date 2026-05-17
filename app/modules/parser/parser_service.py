from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.lib.ai.graphs.pdf_graph import build_pdf_graph
from app.lib.config import settings
from app.lib.storage.storage_service import StorageService
from app.modules.parser.parser_repository import ParserRepository


async def parse_pdfs(db: Session, files: list[UploadFile]) -> dict[str, str]:
    storage_id = str(uuid4())
    storage_svc = StorageService()
    stored_files = await storage_svc.store_many(files, key=f"parse_requests/{storage_id}")

    repository = ParserRepository(db)
    parse_request = repository.create_parse_request(storage_id, stored_files)

    if settings.job_queue_enabled:
        from app.modules.parser.jobs import process_parser_job

        process_parser_job.send(parse_request.id)

    return {
        "message": "ok",
    }


def process_parser_job_by_id(db: Session, request_id: int) -> None:
    repository = ParserRepository(db)
    parse_request = repository.mark_processing(request_id)

    if parse_request is None:
        return

    try:
        parse_request = repository.get_parse_request_with_files(request_id)
        if parse_request is None or not parse_request.parser_files:
            raise ValueError("No parser files found for parse request.")

        graph = build_pdf_graph()
        for parser_file in parse_request.parser_files:
            graph.invoke({"pdf_path": parser_file.url})

        print("doing job")
        repository.mark_processed(request_id)
    except Exception as exc:
        repository.mark_failed(request_id, str(exc))
        raise
