from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.lib.alembic.parse_request_model import ParseRequest, ParseRequestStatus
from app.lib.alembic.parser_file_model import ParserFile
from app.lib.db import Base
from app.lib.di.db import get_db
from app.lib.storage.storage_service import StoredFile
from app.main import app
from app.modules.parser import parser_service
from app.modules.parser.parser_service import process_parser_job_by_id

client = TestClient(app)

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(engine)


def override_get_db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_db] = override_get_db


def test_parse_pdf_files() -> None:
    class FakeStorageService:
        async def store_many(self, files, key):
            return [
                StoredFile(
                    original_name=file.filename or "file",
                    stored_name=file.filename or "file",
                    stored_path=f"storage/{key}/{file.filename}",
                    content_type=file.content_type,
                    size=len(await file.read()),
                    key=f"{key}/{file.filename}",
                )
                for file in files
            ]

    original_storage_service = parser_service.StorageService
    parser_service.StorageService = FakeStorageService

    with Session(engine) as session:
        session.query(ParserFile).delete()
        session.query(ParseRequest).delete()
        session.commit()

    try:
        response = client.post(
            "/parser",
            files=[
                ("files", ("first.pdf", b"%PDF-1.4 first", "application/pdf")),
                ("files", ("second.pdf", b"%PDF-1.4 second", "application/pdf")),
            ],
        )
    finally:
        parser_service.StorageService = original_storage_service

    assert response.status_code == 200
    body = response.json()

    assert body["message"] == "ok"

    with Session(engine) as session:
        parse_request = session.scalar(select(ParseRequest))
        parser_files = session.scalars(select(ParserFile)).all()

    assert parse_request is not None
    assert isinstance(parse_request.id, int)
    assert parse_request.storage_id
    assert parse_request.status == ParseRequestStatus.pending
    assert len(parser_files) == 2
    assert all(parser_file.parse_request_id == parse_request.id for parser_file in parser_files)
    assert all(
        parser_file.key.startswith(f"parse_requests/{parse_request.storage_id}/")
        for parser_file in parser_files
    )


def test_process_parser_job_marks_job_completed() -> None:
    class FakeGraph:
        def __init__(self) -> None:
            self.invocations: list[dict] = []

        def invoke(self, state: dict) -> dict:
            self.invocations.append(state)
            return {"normalized_data": {"source_file": state["pdf_path"]}}

    fake_graph = FakeGraph()
    original_build_pdf_graph = parser_service.build_pdf_graph
    parser_service.build_pdf_graph = lambda: fake_graph

    with Session(engine) as session:
        session.query(ParserFile).delete()
        session.query(ParseRequest).delete()
        session.commit()

        parse_request = ParseRequest(status=ParseRequestStatus.pending)
        session.add(parse_request)
        session.flush()
        session.add(
            ParserFile(
                key=f"parse_requests/{parse_request.storage_id}/first.pdf",
                url=f"storage/parse_requests/{parse_request.storage_id}/first.pdf",
                parse_request_id=parse_request.id,
                size=123,
            )
        )
        session.commit()
        session.refresh(parse_request)
        request_id = parse_request.id

    try:
        with Session(engine) as session:
            process_parser_job_by_id(session, request_id)
    finally:
        parser_service.build_pdf_graph = original_build_pdf_graph

    with Session(engine) as session:
        parse_request = session.scalar(select(ParseRequest).where(ParseRequest.id == request_id))

    assert parse_request is not None
    assert parse_request.status == ParseRequestStatus.processed
    assert parse_request.started_at is not None
    assert parse_request.finished_at is not None
    assert parse_request.expires_at is not None
    assert fake_graph.invocations == [
        {"pdf_path": f"storage/parse_requests/{parse_request.storage_id}/first.pdf"}
    ]
