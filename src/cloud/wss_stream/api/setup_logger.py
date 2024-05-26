import configparser
import logging
from logging.handlers import RotatingFileHandler
import os

from pydantic import BaseModel

from api.get_env import get_env_info


class EnvInfo(BaseModel):
    LOGGER_CONFIG_PATH: str = "logger.ini"


env_info: EnvInfo = get_env_info(EnvInfo)


class LoggerInfo(BaseModel):
    level: str
    folder: str
    file: str
    format: str
    max_bytes: int
    backup_count: int


def load_logger_config(config_path: str) -> LoggerInfo:
    config = configparser.ConfigParser()
    config.read(config_path)

    level = config.get("logger", "Level")
    folder = config.get("logger", "Folder")
    file = config.get("logger", "File")
    format = config.get("logger", "Format")
    max_bytes = config.getint("logger", "MaxBytes")
    backup_count = config.getint("logger", "BackupCount")

    return LoggerInfo(
        level=level,
        folder=folder,
        file=file,
        format=format,
        max_bytes=max_bytes,
        backup_count=backup_count,
    )


def setup_logger(module_name: str, config_path: str = env_info.LOGGER_CONFIG_PATH):
    logger_info = load_logger_config(config_path)

    if not os.path.exists(logger_info.folder):
        os.makedirs(logger_info.folder)

    full_log_path = os.path.join(logger_info.folder, logger_info.file)

    logger = logging.getLogger(module_name)
    logger.setLevel(logging.getLevelName(logger_info.level))

    handler = RotatingFileHandler(
        full_log_path,
        maxBytes=logger_info.max_bytes,
        backupCount=logger_info.backup_count,
    )
    formatter = logging.Formatter(logger_info.format)
    handler.setFormatter(formatter)

    if not logger.handlers:  # Avoid adding multiple handlers to the same logger
        logger.addHandler(handler)

    def log_decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(f"Function {func.__name__} started")
            result = func(*args, **kwargs)
            logger.info(f"Function {func.__name__} finished")
            return result

        return wrapper

    return logger, log_decorator


# Example usage in other modules:
# from api.setup_logger import setup_logger
# logger, log_decorator = setup_logger(__name__)
