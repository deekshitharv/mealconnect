import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """Configure how log lines look. Called once when the app starts."""
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger named 'mealconnect.<name>'."""
    return logging.getLogger(f"mealconnect.{name}")