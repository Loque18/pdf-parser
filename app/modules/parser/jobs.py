import dramatiq

from app.lib import broker  # noqa: F401


@dramatiq.actor(queue_name="parser")
def process_parser_job(file_names: list[str]) -> None:
    _ = file_names
