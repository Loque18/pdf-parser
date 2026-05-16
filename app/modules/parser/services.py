from fastapi import UploadFile

from app.lib.config import settings
from app.modules.parser.jobs import process_parser_job


async def parse_pdfs(files: list[UploadFile]) -> dict[str, str]:
    if settings.job_queue_enabled:
        process_parser_job.send([file.filename for file in files])

    return {
        "message": "ok",
    }
