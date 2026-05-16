from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.lib.alembic.job_model import Job, JobStatus
from app.lib.db import Base
from app.lib.di.db import get_db
from app.main import app
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
    with Session(engine) as session:
        session.query(Job).delete()
        session.commit()

    response = client.post(
        "/parser",
        files=[
            ("files", ("first.pdf", b"%PDF-1.4 first", "application/pdf")),
            ("files", ("second.pdf", b"%PDF-1.4 second", "application/pdf")),
        ],
    )

    assert response.status_code == 200
    body = response.json()

    assert body["message"] == "ok"
    assert body["status"] == "queued"
    assert body["job_id"]

    with Session(engine) as session:
        job = session.scalar(select(Job).where(Job.id == body["job_id"]))

    assert job is not None
    assert job.status == JobStatus.queued


def test_process_parser_job_marks_job_completed() -> None:
    with Session(engine) as session:
        session.query(Job).delete()
        session.commit()

        job = Job(status=JobStatus.queued)
        session.add(job)
        session.commit()
        session.refresh(job)
        job_id = job.id

    with Session(engine) as session:
        process_parser_job_by_id(session, job_id)

    with Session(engine) as session:
        job = session.scalar(select(Job).where(Job.id == job_id))

    assert job is not None
    assert job.status == JobStatus.completed
    assert job.started_at is not None
    assert job.finished_at is not None
    assert job.expires_at is not None
