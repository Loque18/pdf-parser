from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from app.lib.config import settings
from app.lib.logging import logger, setup_logging
from app.modules.health.router import router as health_router
from app.modules.parse_request.root.parse_request_root_router import (
    router as parser_router,
)

setup_logging()


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router, tags=["health"])
    app.include_router(parser_router, prefix="/parser", tags=["parser"])
    app.openapi = lambda: custom_openapi(app)

    @app.on_event("startup")
    async def log_startup() -> None:
        logger.info(
            "Application started",
            app_name=settings.app_name,
            version=settings.app_version,
        )

    return app


def custom_openapi(app: FastAPI) -> dict:
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    parser_body = openapi_schema["components"]["schemas"].get(
        "Body_parse_pdf_files_parser_post"
    )
    if parser_body:
        files_field = parser_body["properties"].get("files")
        if files_field and "items" in files_field:
            files_field["items"] = {
                "type": "string",
                "format": "binary",
            }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = create_application()
