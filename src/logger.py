import logging
import logging.handlers
import os
from typing import Union

# Name for logger
logger_name = "proxy_checker"

def setup_logger(path: str = "../logs", max_bytes: int = 5000000, backup_count: int = 10,
                 level: Union[int, str] = logging.INFO, logger_file: str = logger_name) -> logging.Logger:
    """
    :param path: Path to dir for saving logs
    :param max_bytes: Max size of log file in bytes
    :param backup_count: Max count of log files
    :param level: Logging level
    :param logger_file: Name of file to write logs
    :return: Logger object
    """
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    dir_name = os.path.dirname(__file__)
    handler = logging.handlers.RotatingFileHandler(f"{os.path.join(dir_name, path)}/{logger_file}.log",
                                                   maxBytes=max_bytes, backupCount=backup_count)
    handler.setFormatter(formatter)
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
