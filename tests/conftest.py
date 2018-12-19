'''Configurations for all tests'''

import os
import pytest


@pytest.fixture(scope='session')
def data_dir():
    '''
    Fixture path to test data directory for files
    relating to test
    '''
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    dirpath = os.path.join(curr_dir, 'test-data')
    return dirpath
