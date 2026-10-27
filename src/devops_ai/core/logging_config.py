import logging


def configure_logging(level: str = "INFO") -> None:
    normalized_level = level.upper()
    resolved_level = getattr(logging, normalized_level, None)

    if not isinstance(resolved_level, int):
        raise ValueError(f"Invalid logging level: {level}")

    logging.basicConfig(
        level=resolved_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        force=True,
    )