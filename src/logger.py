import logging
import logging.handlers
import os

logger_name = "proxy_checker"

def setup_logger(path: str = "../logs", max_bytes: int = 5000000, backup_count = 10, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    dir_name = os.path.dirname(__file__)
    handler = logging.handlers.RotatingFileHandler(f"{os.path.join(dir_name, path)}/{logger_name}.log",
                                                   maxBytes=max_bytes, backupCount=backup_count)
    handler.setFormatter(formatter)
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
