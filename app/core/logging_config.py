import logging
import sys

from app.core.config import get_settings


def setup_logging():
    """Configure logging to output to the console only."""
    logging.basicConfig(
        level=get_settings().LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],  # Console only
    )
