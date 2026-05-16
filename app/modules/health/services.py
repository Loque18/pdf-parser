from app.lib.config import settings
from app.modules.health.dtos import HealthResponse


def get_health_status() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
    )
