'''
Readers provide functionality for reading various files. These include
- CSV
- Excel
- Config/INI
'''

import io
from collections import namedtuple
import logging

import requests
import pandas as pd
from . import core, exceptions


LOGGER = logging.getLogger('dropboxutils')


#CSV:

CSVReadConfig = namedtuple(
    'CSVReadConfig',
    [
        'seperator',
        'expected_columns',
        'df_columns',
        'index_col'
    ]
)


def read_csv(filepath: str, csv_read_config: CSVReadConfig) -> pd.DataFrame:
    '''
    Read CSV from a url
    ARGS:
        filepath: Path to the file to be read
        csv_read_config: File configurations for reading the csv file
    '''
    dropbox_link = make_file_link(filepath)
    bytes_io = download_bytes_io(dropbox_link)
    df = read_csv_from_bytes_io(bytes_io, csv_read_config)
    return df


def read_csv_from_bytes_io(bytes_io: io.BytesIO, csv_read_config: csv_read_config) -> pd.DataFrame:
    '''
    Read CSV from a bytes io instance
    ARGS:
        bytes_io: A bytes IO instance
        csv_read_config: File configurations for reading the csv file
    RETURNS:
        df: Resulting pandas dataframe
    '''
    df = pd.read_csv(bytes_io, sep=csv_read_config.seperator)
    df.columns = df.columns.astype('str')
    df.columns = df.columns.str.upper()
    expected_cols = csv_read_config.expected_columns
    df_cols = csv_read_config.df_columns

    if expected_cols is not None:
        validate_columns(df, expected_cols)
        df = df[expected_cols]
    if df_cols is not None:
        df = df.rename(columns=dict(zip(df.columns, df_cols)))
    if csv_read_config.index_col is not None:
        df = df.set_index(csv_read_config.index_col)

    return df


# Excel

ExcelReadConfig = namedtuple(
    'ExcelReadConfig',
    [
        'sheet_name',
        'header_row',
        'expected_columns',
        'df_columns',
        'index_col',
    ]
)


def read_excel(filepath: str, excel_read_config: ExcelReadConfig):
    pass


def read_excel_from_bytes_io(bytes_io: io.BytesIO, excel_read_config: ExcelReadConfig):
    pass


# Validation

def validate_columns(df, expected_columns):
    '''
    Validate dataframe columns otherwise raise an appropriate
    exceptions
    ARGS:
        df: Dataframe to be validated
        expected_columns: Expected columns in the csv file
    '''
    distinct_cols = set(expected_columns) - df.columns
    if distinct_cols:
        raise exceptions.ReaderException('Invalid cols - {}'.format(distinct_cols))
    LOGGER.debug('Dataframe validated')


# Common

def make_file_link(filepath: str, max_tries=5) -> str:
    tries_count = 0
    while True:
        try:
            tries_count += 1
            link = core.make_file_link(filepath)
            return link
        except exceptions.DropboxException as err:
            LOGGER.warning(err)
            if tries_count >= max_tries:
                raise
        else:
            break


def download_bytes_io(link, read_timeout=10):
    try:
        filedata = io.BytesIO(requests.get(link, timout=read_timeout).content)
    except requests.exceptions.RequestsException as err:
        raise exceptions.DownloadException(err)
    return filedata
