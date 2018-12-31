'''
Test logging related functions
'''

#pylint: disable=redefined-outer-name, missing-docstring

import logging
import pytest
from dropboxutils import logger


# Fixtures


@pytest.fixture(scope='module')
def app_logger():
    logger = logging.getLogger('test')
    logger.setLevel(logging.DEBUG)
    return logger


# Tests

def test_logger(app_logger):
    '''Test flushing on the buffering logger'''
    capacity = 4
    buff_handler = logger.IOHandler(capacity)
    formatter = logging.Formatter(logger.FORMAT)
    buff_handler.setFormatter(formatter)
    buff_handler.setLevel(logging.DEBUG)

    app_logger.addHandler(buff_handler)
    for _ in range(capacity):
        app_logger.debug('Logging a debug message')
