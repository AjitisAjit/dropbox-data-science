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


def read_csv(filepath: str, csv_read_config: CSVReadConfig):
    dropbox_link = make_file_link(filepath)
    bytes_io = download_bytes_io(dropbox_link)
    df = read_csv_from_bytes_io(bytes_io, csv_read_config)
    return df


def read_csv_from_bytes_io(bytes_io: io.BytesIO, csv_read_config: csv_read_config):
    df = pd.read_csv(bytes_io, sep=csv_read_config.seperator)
    df.columns = df.columns.astype('str')
    df.columns = df.columns.str.upper()

    try:
        validate_columns(df, csv_read_config)
    except (ValueError, AssertionError, AttributeError) as err:
        raise exceptions.RaiseReaderException(err)

    if csv_read_config.output_dataframe_columns:
        df = df.rename(columns=dict(
            zip(csv_read_config.expected_columns, csv_read_config.df_columns)
        ))
    if csv_read_config.index_col is not None:
        dataframe = df.set_index(csv_read_config.index_col)

    return dataframe


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

def validate_columns(df, read_config):
    if read_config.expected_columnns:
        if not all(c in df.columns for c in read_config.expected_columns):
            distinct_columns = set(read_config.expected_columns) - df.columns
            raise AssertionError('Invalid columns - {}'.format(distinct_columns))
        df = df[read_config.expected_columns]
    else:
        LOGGER.warning('No input columns specified, skipping validation')


def rename_dataframe_columns(dataframe, input_columns, output_columns):
    '''Rename_dataframe columns based on the result expected in output'''
    dataframe = dataframe.rename(columns=dict(zip(input_columns, output_columns)))
    return dataframe


# Common

def make_file_link(filepath: str, max_tries=5) -> str:
    tries_count = 0
    while True:
        try:
            tries_count += 1
            link = core.make_file_link(filepath)
            return link
        except exceptions.DropboxException as err:
            LOGGER.warning('Unable to create file link - %s, retrying', filepath)
            if tries_count >= max_tries:
                raise exceptions.MakeUrlException('Error creating file link - %s', filepath)
        else:
            break


def download_bytes_io(link, read_timeout=10):
    try:
        filedata = io.BytesIO(requests.get(link, timout=read_timeout).content)
    except requests.exceptions.RequestsException as err:
        raise exceptions.DownloadException(
            'Data could not be read from URL - {} - {}'.format(url, err)
        )
    return filedata
