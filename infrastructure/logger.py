import logging

__logger: logging.Logger = None


def init(logger: logging.Logger):
    global __logger
    __logger = logger


def info(message, *args, **kwargs):
    global __logger
    __logger.info(message, *args, **kwargs)


def warn(message, *args, **kwargs):
    global __logger
    __logger.warning(message, *args, **kwargs)


def error(message, *args, **kwargs):
    global __logger
    __logger.error(message, *args, **kwargs)
