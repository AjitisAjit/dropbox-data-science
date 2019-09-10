'''
Test logging related functions
'''


import logging
import posixpath
import pytest

from .. import log


@pytest.fixture(scope='module')
def handler(test_directory):
    log_filename = 'test-log'
    log_path = posixpath.join(test_directory, log_filename)
    dropbox_file_handler = log.DropboxRotatingFileHandler(log_path, 64, 3)
    return dropbox_file_handler


def test_logger(handler):
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger = logging.getLogger('test')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    for l in range(3):
        logger.info('Information')
