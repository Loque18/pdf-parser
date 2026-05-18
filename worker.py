from dotenv import load_dotenv
load_dotenv()

from app.lib.logging import setup_logging
from app.modules.parse_request import jobs  # noqa: F401

setup_logging()
