'''
Test writers
'''

#pylint: disable=redefined-outer-name, missing-docstring

import os
import io
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
def excel_write_config(data_dir):
    config_file = os.path.join(data_dir, 'excel_write.yaml')
    return config_file

# Tests

def test_write_csv(test_df):
    buffer = writers.csv_to_buffer(test_df, index=False)
    assert isinstance(buffer, io.StringIO)
    assert buffer.getvalue()
    assert isinstance(buffer, io.StringIO)


def test_write_excel(test_df, excel_write_config):
    excel_dfs = [test_df] # Since excel file has a single dataframe
    buffer = writers.excel_to_buffer(excel_dfs, excel_write_config)
    assert isinstance(buffer, io.BytesIO)
    assert buffer.getvalue()
