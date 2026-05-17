from pydantic import BaseModel

from app.lib.storage.storage_service import StoredFile

class CreateRequestDto(BaseModel):
    storage_id: str
    stored_files: list[StoredFile]

