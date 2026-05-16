from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from app.modules.parser.services import parse_pdfs

router = APIRouter()


@router.post("", summary="Parse PDF files")
async def parse_pdf_files(
    files: Annotated[list[UploadFile], File(description="PDF files to parse")],
) -> dict[str, str]:
    return await parse_pdfs(files)
