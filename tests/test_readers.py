'''
Test readers
'''

#pylint: disable=redefined-outer-name, missing-docstring

import io
import configparser

import pytest
import numpy as np
import pandas as pd

from dropboxutils import readers


# Create bytes io instances

@pytest.fixture(scope='module')
def test_df():
    dims = 5
    df = pd.DataFrame(np.random.randn(dims, dims))
    return df


@pytest.fixture(scope='module')
def csv_buffer(test_df):
    buffer = io.StringIO()
    test_df.to_csv(buffer, index=False)
    buffer = io.BytesIO(bytes(buffer.getvalue(), 'utf8'))
    return buffer


@pytest.fixture(scope='module')
def config_buffer():
    config = configparser.ConfigParser()
    config['MY_SECTION'] = {
        'configA': 'Some value',
        'configB': 'Another value'
    }

    buffer = io.StringIO()
    config.write(buffer)
    buffer = io.BytesIO(bytes(buffer.getvalue(), 'utf8'))
    return buffer


@pytest.fixture(scope='module')
def excel_buffer(test_df):
    buffer = io.BytesIO()
    writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
    test_df.to_excel(writer)
    writer.save()
    return buffer


# Tests

def test_read_csv_buffer(csv_buffer):
    csv_config = readers.make_csv_read_config()
    read_df = readers.read_csv_from_buffer(csv_buffer, csv_config)
    assert not read_df.empty


def test_read_config_buffer(config_buffer):
    config = readers.read_config_from_buffer(config_buffer)
    sections = config.sections()
    assert len(sections) == 1


def test_read_excel(excel_buffer):
    excel_config = readers.make_excel_read_config()
    read_df = readers.read_excel_from_buffer(excel_buffer, excel_config)
    assert not read_df.empty
