'''
Test writers
'''

#pylint: disable=redefined-outer-name, missing-docstring

import io
import os
import yaml

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


@pytest.fixture(scope='module')
def yaml_file():
    yaml_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'test-data',
        'excel-write.yaml'
    )
    return yaml_path


@pytest.fixture(scope='module')
def excel_write_config(yaml_file):
    pass


# Tests

def test_write_csv(test_df):
    write_config = writers.make_csv_write_config()
    buffer = writers.csv_to_buffer(test_df, write_config)
    assert isinstance(buffer, io.StringIO)
    assert buffer.getvalue()


def test_write_excel(test_df, excel_write_config):
    pass
