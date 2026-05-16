from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


@dataclass(slots=True)
class StoredFile:
    original_name: str
    stored_name: str
    stored_path: str
    content_type: str | None
    size: int
    key: str | None = None


class StorageService:
    def __init__(self, local_dir: str = "storage") -> None:
        self.base_dir = Path(local_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def store(
        self,
        key: str,
        file: UploadFile,
    ) -> StoredFile:
        original_name = file.filename or "file"
        target_path = self._resolve_path(key)

        data = await file.read()
        target_path.write_bytes(data)
        await file.seek(0)

        return StoredFile(
            original_name=original_name,
            stored_name=Path(key).name,
            stored_path=str(target_path),
            content_type=file.content_type,
            size=len(data),
            key=key,
        )

    async def store_many(
        self,
        files: list[UploadFile],
        key: str,
    ) -> list[StoredFile]:
        stored_files: list[StoredFile] = []
        for file in files:
            original_name = file.filename or "file"
            stored_name = self._build_file_name(original_name)
            file_key = f"{key.rstrip('/')}/{stored_name}"
            stored_files.append(await self.store(file_key, file))
        return stored_files

    def delete_file(self, stored_path: str) -> None:
        path = Path(stored_path)
        if path.exists():
            path.unlink()

    def _resolve_path(self, key: str) -> Path:
        target_path = self.base_dir / key
        target_path.parent.mkdir(parents=True, exist_ok=True)
        return target_path

    def _build_file_name(self, original_name: str) -> str:
        suffix = Path(original_name).suffix
        return f"{uuid4()}{suffix}"
