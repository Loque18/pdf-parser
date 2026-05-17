from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.lib.alembic.parse_job_model import ParseJob
from app.lib.alembic.parse_request_model import ParseRequest, ParseRequestStatus
from app.lib.alembic.request_file_model import RequestFile
from app.lib.alembic.parser_output_model import ParserOutput
from app.lib.db import Base
from app.lib.di.db import get_db
from app.lib.storage.storage_service import StoredFile
from app.main import app
from app.modules.parse_request.root import parse_request_job_service
from app.modules.parse_request.root import parse_request_root_service
from app.modules.parse_request.root.parse_request_job_service import (
    process_parse_job,
)

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

    original_storage_service = parser_request_root_service.StorageService
    parser_request_root_service.StorageService = FakeStorageService

    with Session(engine) as session:
        session.query(ParserOutput).delete()
        session.query(ParseJob).delete()
        session.query(RequestFile).delete()
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
        parser_request_root_service.StorageService = original_storage_service

    assert response.status_code == 200
    body = response.json()

    assert body["parse_request"]["id"]
    assert body["parse_request"]["status"] == "pending"

    with Session(engine) as session:
        parse_request = session.scalar(select(ParseRequest))
        request_files = session.scalars(select(RequestFile)).all()
        parse_jobs = session.scalars(select(ParseJob)).all()

    assert parse_request is not None
    assert isinstance(parse_request.id, str)
    assert parse_request.storage_id
    assert parse_request.status == ParseRequestStatus.pending
    assert len(request_files) == 2
    assert len(parse_jobs) == 2
    assert all(request_file.parse_request_id == parse_request.id for request_file in request_files)
    assert all(
        request_file.storage_key.startswith(f"parse_requests/{parse_request.storage_id}/")
        for request_file in request_files
    )
    assert all(parse_job.request_file_id for parse_job in parse_jobs)


def test_process_parser_job_marks_job_completed() -> None:
    class FakeGraph:
        def __init__(self) -> None:
            self.invocations: list[dict] = []

        async def ainvoke(self, state: dict) -> dict:
            self.invocations.append(state)
            return {
                "normalized_data": [
                    {
                        "customer": "ACME Corp",
                        "amount": 100.0,
                        "tax_rate": 19,
                        "tax_amount": 19.0,
                        "total": 119.0,
                    }
                ]
            }

    fake_graph = FakeGraph()
    original_build_pdf_graph = parse_request_job_service.build_pdf_graph
    parse_request_job_service.build_pdf_graph = lambda: fake_graph

    with Session(engine) as session:
        session.query(ParserOutput).delete()
        session.query(ParseJob).delete()
        session.query(RequestFile).delete()
        session.query(ParseRequest).delete()
        session.commit()

        parse_request = ParseRequest(status=ParseRequestStatus.pending)
        session.add(parse_request)
        session.flush()
        request_file = RequestFile(
            original_name="first.pdf",
            key=f"parse_requests/{parse_request.storage_id}/first.pdf",
            url=f"storage/parse_requests/{parse_request.storage_id}/first.pdf",
            parse_request_id=parse_request.id,
            size=123,
        )
        session.add(request_file)
        session.flush()
        session.add(
            ParseJob(
                request_file_id=request_file.id,
            )
        )
        session.commit()
        session.refresh(parse_request)
        request_id = parse_request.id
        parse_job_id = session.scalar(select(ParseJob.id))

    try:
        with Session(engine) as session:
            process_parse_job(session, parse_job_id)
    finally:
        parse_request_job_service.build_pdf_graph = original_build_pdf_graph

    with Session(engine) as session:
        parse_request = session.scalar(select(ParseRequest).where(ParseRequest.id == request_id))
        parser_output = session.scalar(select(ParserOutput))

    assert parse_request is not None
    assert parse_request.status == ParseRequestStatus.processed
    assert parse_request.expires_at is not None
    assert parser_output is not None
    assert parser_output.payload == {
        "items": [
            {
                "customer": "ACME Corp",
                "amount": 100.0,
                "tax_rate": 19,
                "tax_amount": 19.0,
                "total": 119.0,
            }
        ]
    }
    assert fake_graph.invocations == [
        {"pdf_path": f"storage/parse_requests/{parse_request.storage_id}/first.pdf"}
    ]
