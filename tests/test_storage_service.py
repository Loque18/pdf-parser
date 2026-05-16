import asyncio
from io import BytesIO
from pathlib import Path

from fastapi import UploadFile

from app.lib.storage.storage_service import StorageService


def test_store(tmp_path: Path) -> None:
    service = StorageService(str(tmp_path))
    upload = UploadFile(filename="document.pdf", file=BytesIO(b"pdf-content"))

    try:
        stored = asyncio.run(service.store("jobs/1/document.pdf", upload))
    finally:
        upload.file.close()

    stored_path = Path(stored.stored_path)

    assert stored.original_name == "document.pdf"
    assert stored.stored_name == "document.pdf"
    assert stored.size == len(b"pdf-content")
    assert stored_path.exists()
    assert stored_path.read_bytes() == b"pdf-content"
    assert stored_path.parent == tmp_path / "jobs" / "1"


def test_store_many(tmp_path: Path) -> None:
    service = StorageService(str(tmp_path))
    first = UploadFile(filename="first.pdf", file=BytesIO(b"first-content"))
    second = UploadFile(filename="second.txt", file=BytesIO(b"second-content"))

    async def run():
        return await service.store_many([first, second], key="jobs/123")

    try:
        stored_files = asyncio.run(run())
    finally:
        first.file.close()
        second.file.close()

    assert len(stored_files) == 2
    assert stored_files[0].original_name == "first.pdf"
    assert stored_files[1].original_name == "second.txt"
    assert Path(stored_files[0].stored_path).exists()
    assert Path(stored_files[1].stored_path).exists()
    assert Path(stored_files[0].stored_path).parent == tmp_path / "jobs" / "123"
    assert Path(stored_files[1].stored_path).parent == tmp_path / "jobs" / "123"
