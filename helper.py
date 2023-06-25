import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path


def init_logging(log_dir, log_level=logging.DEBUG):
    formatter = logging.Formatter(
        '%(levelname)1.1s %(asctime)s %(message)s',
        datefmt='%H:%M:%S')
    # formatter = logging.Formatter(
    #     '%(levelname)1.1s %(asctime)s %(module)15s:%(lineno)03d %(funcName)15s) %(message)s',
    #     datefmt='%H:%M:%S')
    
    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        log_path = os.path.join(log_dir, "smartcopy.log")
        file_handler = TimedRotatingFileHandler(log_path, when="d")
        file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger()
    if file_handler:
        logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(log_level)

