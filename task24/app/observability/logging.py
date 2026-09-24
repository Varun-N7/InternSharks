import logging
import sys


logger = logging.getLogger("task24")

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger.setLevel(logging.INFO)


def log_ai_event(
    event: str,
    **fields,
) -> None:
    safe_fields = " ".join(
        f"{key}={value}"
        for key, value in fields.items()
    )

    logger.info(
        "event=%s %s",
        event,
        safe_fields,
    )