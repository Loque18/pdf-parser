from typing import Any
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.lib.di.db import get_db
from app.modules.parse_request.root.parse_request_dto import CreateParseRequestResponse
from app.modules.parse_request.root.parse_request_root_service import (
    get_parse_request_by_id,
    parse_pdfs,
)

router = APIRouter()


@router.post("", summary="Parse PDF files", response_model=CreateParseRequestResponse)
async def parse_pdf_files(
    files: Annotated[list[UploadFile], File(description="PDF files to parse")],
    db: Session = Depends(get_db),
) -> CreateParseRequestResponse:
    return await parse_pdfs(db, files)


@router.get("/{request_id}", summary="Get parse request")
def get_parse_request(
    request_id: str,
    db: Session = Depends(get_db),
) -> dict:
    return get_parse_request_by_id(db, request_id)
