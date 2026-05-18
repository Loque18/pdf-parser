from typing import Any
from typing import Annotated

from fastapi import APIRouter, Depends, File, Header, UploadFile
from sqlalchemy.orm import Session

from app.lib.di.db import get_db
from app.modules.parse_request.root.parse_request_dto import (
    CreateParseRequestResponse,
    ListUserParseRequestsResponse,
    RetrieveRequestResponse
)
from app.modules.parse_request.root.parse_request_root_service import (
    get_parse_request_by_id,
    list_parse_requests_by_user_id,
    parse_pdfs,
)

router = APIRouter()


@router.post("", summary="Parse PDF files", response_model=CreateParseRequestResponse)
async def parse_pdf_files(
    files: Annotated[list[UploadFile], File(description="PDF files to parse")],
    client_id: Annotated[str, Header(alias="X-client-Id")],
    db: Session = Depends(get_db),
) -> CreateParseRequestResponse:
    return await parse_pdfs(db, files, client_id)

@router.get("/requests", summary="Get user's parse requests", response_model=ListUserParseRequestsResponse)
def get_my_parse_requests(
    client_id: Annotated[str, Header(alias="X-client-Id")],
    db: Session = Depends(get_db),
) -> ListUserParseRequestsResponse:
    return list_parse_requests_by_user_id(db, client_id)


@router.get("/requests/{request_id}", summary="Get parse request", response_model=RetrieveRequestResponse)
def get_parse_request(
    request_id: str,
    client_id: Annotated[str, Header(alias="X-client-Id")],
    db: Session = Depends(get_db),
) -> RetrieveRequestResponse:
    return get_parse_request_by_id(db, request_id, client_id)
