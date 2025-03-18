import sys
from datetime import datetime
from loguru import logger as _logger
from .config import PROJECT_ROOT

_print_level = "INFO"


def define_log_level(print_level="INFO", logfile_level="DEBUG", name: str = None):
    """Adjust the log level"""
    global _print_level
    _print_level = print_level
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d%H%M%S")
    log_name = (
        f"{name}_{formatted_date}" if name else formatted_date
    )  # name a log with prefix name

    _logger.remove()
    _logger.add(sys.stderr, level=print_level)
    _logger.add(PROJECT_ROOT / f"logs/{log_name}.log",
                level=logfile_level,
                rotation="00:00",
                retention="7 days",
                compression="zip",
                encoding="utf-8"
                )
    return _logger


logger = define_log_level()

if __name__ == "__main__":
    logger.info("Starting application")
    logger.debug("Debug message")
    logger.warning("Warnin message")
    logger.error("Eror message")
    logger.critical("Critical message")

    try:
        raise ValueError("tests Erroe")
    except Exception as e:
        logger.exception(f"An Error accured:{e}")
