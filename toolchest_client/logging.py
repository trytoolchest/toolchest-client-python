from loguru import logger
import os
import sys

LOG_LEVEL = os.environ.get("TOOLCHEST_LOG_LEVEL", "INFO")


def get_log_level():
    return LOG_LEVEL


def setup_logging(log_level=None):
    global LOG_LEVEL
    if log_level and log_level != LOG_LEVEL:
        LOG_LEVEL = log_level
    logger.remove()

    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
    if LOG_LEVEL not in valid_log_levels:
        raise ValueError(f"Invalid log level: {LOG_LEVEL}. Valid levels are: {valid_log_levels}")

    if LOG_LEVEL in ["DEBUG", "INFO", "WARNING"]:
        stdout_filter = lambda record: record["level"].no < 40
        logger.add(
            sys.stdout,
            filter=stdout_filter,
            level=LOG_LEVEL,
            format="<green>{time}</green> | <level>{level}</level> | <level>{message}</level>",
        )
    # Including if log_level == "ERROR"
    logger.add(sys.stderr, level="ERROR")
