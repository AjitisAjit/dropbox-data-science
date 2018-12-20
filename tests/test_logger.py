'''
Test logging related functions
'''

#pylint: disable=redefined-outer-name, missing-docstring

import io
import logging
import pytest
from dropboxutils import logger

# Fixtures

@pytest.fixture(scope='module')
def buffer():
    buffer = io.StringIO()
    return buffer


@pytest.fixture(scope='module')
def app_logger():
    logger = logging.getLogger('test')
    logger.setLevel(logging.DEBUG)
    return logger


# Tests

def test_logger(app_logger, buffer):
    capacity = 4
    buff_handler = logger.BufferHandler(capacity, buffer)
    buff_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(logger.FORMAT)
    buff_handler.setFormatter(formatter)
    app_logger.addHandler(buff_handler)

    for _ in range(capacity):
        app_logger.debug('Logging a debug message')

    assert buffer.getvalue()
