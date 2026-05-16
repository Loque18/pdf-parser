from fastapi import APIRouter

from app.modules.health.dtos import HealthResponse
from app.modules.health.services import get_health_status

router = APIRouter()


@router.get("/health", summary="Health check", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return get_health_status()
