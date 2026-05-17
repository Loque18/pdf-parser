from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.lib.config import settings
from app.modules.health.router import router as health_router
from app.modules.parse_request.root.parse_request_root_router import (
    router as parser_router,
)
from app.modules.post.router import router as post_router


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.include_router(health_router, tags=["health"])
    app.include_router(parser_router, prefix="/parser", tags=["parser"])
    app.include_router(post_router, prefix="/posts", tags=["posts"])
    app.openapi = lambda: custom_openapi(app)
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
