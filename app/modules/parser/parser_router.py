from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.lib.di.db import get_db
from app.modules.parser.parser_service import parse_pdfs

router = APIRouter()


@router.post("", summary="Parse PDF files")
async def parse_pdf_files(
    files: Annotated[list[UploadFile], File(description="PDF files to parse")],
    db: Session = Depends(get_db),
) -> dict[str, str]:
    return await parse_pdfs(db, files)
