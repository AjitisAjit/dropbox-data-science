'''
Test writers
'''

#pylint: disable=redefined-outer-name, missing-docstring

import io

import pytest
import numpy as np
import pandas as pd
from dropboxutils import writers


# Create byte io instances

@pytest.fixture(scope='module')
def test_df():
    dims = 5
    df = pd.DataFrame(np.random.randn(dims, dims))
    return df


# Tests

def test_write_csv(test_df):
    buffer = writers.csv_to_buffer(test_df)
    assert isinstance(buffer, io.StringIO)
    assert len(buffer.getvalue())
