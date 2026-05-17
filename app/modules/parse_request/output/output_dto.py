from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class OutputDTO:
    parse_job_id: str
    status: str
    payload: dict[str, Any] | None = None
    error_message: str | None = None
