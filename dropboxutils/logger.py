'''
Provides functionality to generate a logger that logs
to files on dropbox.
Log format is defined as :
'''
import os
import io
import logging
from logging.handlers import BufferingHandler
from . import writers


FORMAT = '%(levelname)s - %(asctime)s - %(message)s'


class IOHandler(BufferingHandler):
    '''
    Subclasses buffering handler and flushes the result to
    a string io instance
    ARGS:
        capacity: Size of the buffer
    '''

    def __init__(self, capacity):
        self.memory = io.StringIO()
        super().__init__(capacity)

    def flush(self):
        '''
        Writes to memory and clears it if the buffer is
        full or close is called on the logger instance
        '''
        if self.buffer:
            self.write_memory()
            self.reset_memory()

    def write_memory(self):
        '''
        Writes the messages to a string IO instance in memory
        '''
        msg_list = [self.format(rec) for rec in self.buffer]
        for msg in msg_list:
            self.memory.write(msg)

    def reset_memory(self):
        '''Reset string_io instance'''
        self.memory = io.StringIO()


class DropboxHandler(IOHandler):
    '''
    Subclasses StringIOHandler and flushes the
    result to a timestamped path on dropbox
    ARGS:
        outpath: Path on dropbox to which the logs are written
        capacity: Capacity of the buffer
    '''

    def __init__(self, capacity, outpath):
        self.outpath = outpath
        super().__init__(capacity)

    def flush(self):
        '''
        Writes to a timestamped path on dropbox if the
        buffer is full or close is called
        '''
        if self.buffer:
            self.write_memory()
            self.write_to_dropbox()
            self.reset_memory()

    def write_to_dropbox(self):
        '''
        Writes memory contents to a path on dropbox
        '''
        encoding = 'utf8'
        bytes_data = bytes(self.memory.getvalue(), encoding)
        outpath = writers.timestamp_path(self.outpath)
        writers.bytes_to_dropbox(bytes_data, outpath)


def make_stream_handler(stream=None):
    '''
    Make StreamHandler instance with appropriate level and formatting
    information
    ARGS:
        stream: Where StreamHandler outputs the result
    '''
    formatter = logging.Formatter(FORMAT)
    stream_handler = logging.StreamHandler(stream=stream)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)
    return stream_handler


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
