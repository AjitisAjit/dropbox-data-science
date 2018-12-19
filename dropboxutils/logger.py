'''
Provides functionality to generate a logger that logs
to files on dropbox.
Log format is defined as :
'''
import os
import io
import logging
from logging.handlers import MemoryHandler
from . import writers


FORMAT = '%(levelname)s - %(asctime)s - %(message)s'


class DropboxHandler(MemoryHandler):
    '''
    A memory handler that flushes the log messages to
    a Stream Handler when the capacity is exceeded.

    Level - Timestamp - Log message
    '''

    def __init__(self, path, capacity):
        self.path = path
        self.buffer = io.StringIO()
        self.set_target()
        super().__init__(capacity)

    def flush(self):
        super().flush()
        self.write_logs()
        if self.target is not None:
            self.target.close()
        self.set_target()

    def write_logs(self):
        '''Write logs to dropbox'''
        data = self.buffer.getvalue() # Get bytes from string IO
        if data:
            writers.write_text(data, self.path, ts=True)

    def set_target(self):
        self.buffer = io.StringIO()
        formatter = logging.Formatter(FORMAT)
        stream_handler = logging.StreamHandler(self.buffer)
        stream_handler.setFormatter(formatter)
        self.setTarget(stream_handler)


def make_dropbox_handler(logging_dir: str, level: str, capacity: int = 100) -> logging.Handler:
    '''
    Create dropbox logger
    ARGS:
        logging_dir: Directory where debug logs are stored
        level: Logging level
        logger capacity
    '''
    filename = 'debug.log'
    path = os.path.join(logging_dir, filename)
    handler = DropboxHandler(path, capacity)
    handler.setLevel(level)
    formatter = logging.Formatter(FORMAT)
    handler.setFormatter(formatter)
    return handler


def create_logger(logger_name: str, logging_dir: str) -> logging.Logger:
    '''
    Create a dropbox logger. The logger has the following
    settings for different levels:
    INFO - StreamHandler
    DEBUG - DropboxHandler - Capacity - 100
    WARNING - DropboxHandler - Capacity - 10
    ERROR - DropboxHandler - Capacity - 10
    '''
    info_handler = make_info_handler()
    debug_handler = make_dropbox_handler(logging_dir, logging.DEBUG, 100)
    warning_handler = make_dropbox_handler(logging_dir, logging.WARNING, 10)
    error_handler = make_dropbox_handler(logging_dir, logging.ERROR, 10)
    silence_dropbox_api_logger()

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(info_handler)
    logger.addHandler(debug_handler)
    logger.addHandler(warning_handler)
    logger.addHandler(error_handler)

    return logger


def make_info_handler() -> logging.Handler:
    '''
    Info handler prints to console
    '''
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(FORMAT)
    handler.setFormatter(formatter)
    return handler


def silence_dropbox_api_logger(level=logging.WARNING):
    '''
    Silence dropbox logging setting level to appropriate
    high level (Warning by default)
    '''
    logging.getLogger('dropbox').setLevel(level)
    logging.getLogger('requests').setLevel(level)
    logging.getLogger('urllib3').setLevel(level)

