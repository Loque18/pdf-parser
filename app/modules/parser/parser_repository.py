from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.lib.alembic.job_model import Job, JobStatus


class ParserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_job(self) -> Job:
        job = Job(status=JobStatus.queued)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_job(self, job_id: str) -> Job | None:
        return self.db.get(Job, job_id)

    def mark_running(self, job_id: str) -> Job | None:
        job = self.get_job(job_id)
        if job is None:
            return None

        job.status = JobStatus.running
        job.started_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(job)
        return job

    def mark_completed(self, job_id: str, result_location: str | None = None) -> Job | None:
        job = self.get_job(job_id)
        if job is None:
            return None

        now = datetime.now(timezone.utc)
        job.status = JobStatus.completed
        job.result_location = result_location
        job.finished_at = now
        job.expires_at = now + timedelta(hours=24)
        self.db.commit()
        self.db.refresh(job)
        return job

    def mark_failed(self, job_id: str, error_message: str) -> Job | None:
        job = self.get_job(job_id)
        if job is None:
            return None

        now = datetime.now(timezone.utc)
        job.status = JobStatus.failed
        job.error_message = error_message
        job.finished_at = now
        job.expires_at = now + timedelta(hours=24)
        self.db.commit()
        self.db.refresh(job)
        return job
