from fastapi import FastAPI

from app.lib.config import settings
from app.modules.health.router import router as health_router
from app.modules.post.router import router as post_router


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.include_router(health_router, tags=["health"])
    app.include_router(post_router, prefix="/posts", tags=["posts"])
    return app


app = create_application()
