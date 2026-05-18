from pydantic import BaseModel

from app.lib.storage.storage_service import StoredFile

class CreateRequestDto(BaseModel):
    storage_id: str
    stored_files: list[StoredFile]


# ==================================================
# RESPONSES
# ==================================================

class CreateParseRequestResponse(BaseModel):
    id: str
    status: str
    created_at: str
    expires_at: str | None
