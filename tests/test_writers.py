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
    with open(config_file, 'rt') as conf:
        sheet_configs = list(filter(lambda x: x is not None, yaml.load_all(conf)))

    return sheet_configs

# Tests

def test_write_csv(test_df):
    write_config = writers.make_csv_write_config()
    buffer = writers.csv_to_buffer(test_df, write_config)
    assert isinstance(buffer, io.StringIO)
    assert buffer.getvalue()


def test_write_excel(test_df, excel_write_config):
    excel_dfs = [test_df] # Since excel file has a single dataframe
    buffer = writers.excel_to_buffer(excel_dfs, excel_write_config)
    assert buffer.getvalue()
