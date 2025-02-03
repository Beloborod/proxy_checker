import logging
from src.logger import setup_logger


def test_logger():
    assert type(setup_logger()) is logging.Logger
