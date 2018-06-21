import logging

from logging.handlers import RotatingFileHandler


def get_logger(LOG_FILE):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(filename)s :: %(funcName)s :: %(lineno)s :: %(message)s')

    file_handler = RotatingFileHandler(LOG_FILE, 'a', 1000000, 1)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger
