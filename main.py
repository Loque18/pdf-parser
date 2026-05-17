import uvicorn

from app.main import app
from app.lib.logging import setup_logging


if __name__ == "__main__":
    setup_logging()
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_config=None,
    )
