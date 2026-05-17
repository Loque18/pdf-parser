import asyncio

from sqlalchemy.orm import Session

from app.lib.ai.graphs.pdf_graph import build_pdf_graph
from app.modules.parse_request.output.output_dto import OutputDTO
from app.modules.parse_request.output.output_repository import OutputRepository
from app.modules.parse_request.root.parse_request_root_repository import (
    ParseRequestRootRepository,
)


def process_parse_request_job(db: Session, request_id: str) -> None:
    asyncio.run(_process_parse_request_job(db, request_id))


async def _process_parse_request_job(db: Session, request_id: str) -> None:
    repository = ParseRequestRootRepository(db)
    output_repository = OutputRepository(db)
    parse_request = repository.mark_processing(request_id)

    if parse_request is None:
        return

    try:
        parse_request = repository.get_parse_request_with_files(request_id)
        if parse_request is None or not parse_request.parser_files:
            raise ValueError("No parser files found for parse request.")

        graph = build_pdf_graph()
        for parser_file in parse_request.parser_files:
            result = await graph.ainvoke({"pdf_path": parser_file.url})
            output_dto = OutputDTO(
                parser_file_id=parser_file.id,
                status="processed",
                payload={"items": result.get("normalized_data", [])},
            )
            if output_repository.get_by_parser_file_id(parser_file.id) is None:
                output_repository.create_output(output_dto)
            else:
                output_repository.mark_processed(output_dto)

        print("doing job")
        repository.mark_processed(request_id)
    except Exception as exc:
        if parse_request is not None and parse_request.parser_files:
            for parser_file in parse_request.parser_files:
                failed_output = OutputDTO(
                    parser_file_id=parser_file.id,
                    status="failed",
                    error_message=str(exc),
                )
                if output_repository.get_by_parser_file_id(parser_file.id) is None:
                    output_repository.create_output(failed_output)
                else:
                    output_repository.mark_failed(failed_output)
        repository.mark_failed(request_id, str(exc))
        raise
