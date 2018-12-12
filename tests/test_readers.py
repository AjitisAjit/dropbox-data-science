'''
Test readers
'''
import io
import configparser

import pytest
import numpy as np
import pandas as pd

from dropboxutils import readers


# Create files


@pytest.fixture(scope='module')
def test_df():
    dims = 5
    df = pd.DataFrame(np.random.randn(dims, dims))
    return df


@pytest.fixture(scope='module')
def csv_bytes_io(test_df):
    bytes_io = io.BytesIO(test_df)
    return bytes_io


def test_read_csv_bytes_io(csv_bytes_io, test_df):
    read_df = readers.read_csv_from_bytes_io(csv_bytes_io)
    assert read_df == test_df
