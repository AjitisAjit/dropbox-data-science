'''
Readers provide functionality for reading various files. These include
- CSV
- Excel
- Config/INI
'''

import io
import logging
import configparser

from typing import List
from collections import namedtuple

import requests
import pandas as pd
from . import core, exceptions


LOGGER = logging.getLogger('dropboxutils')


# Config/INI

def read_config(dropbox_path: str) -> configparser.ConfigParser:
    '''
    Read an ini file into a config parser instance
    ARGS:
        filepath: Path to file to be read
    RETURNS:
        config: ConfigParser instance read
    '''
    buffer = dropbox_to_buffer(dropbox_path)
    config = read_config_from_buffer(buffer)
    return config


def read_config_from_buffer(buffer: io.BytesIO) -> configparser.ConfigParser:
    '''
    Read configuratiojn file from bytes IO instance
    ARGS:
        bytes_io: A bytes io instance
    RETURNS:
        config: ConfigParser instance read
    '''
    config = configparser.ConfigParser()
    string = buffer.getvalue().decode('utf8')
    config.read_string(string)
    return config


# CSV:

def make_csv_config(
        seperator: str = ',',
        expected_cols: List = None,
        df_cols: List = None,
        index_col: str = None) -> object:
    '''CSV config constructor'''
    CSVReadConfig = namedtuple(
        'CSVReadConfig',
        [
            'seperator',
            'expected_cols',
            'df_cols',
            'index_col'
        ]
    )
    return CSVReadConfig(
        seperator=seperator,
        expected_cols=expected_cols,
        df_cols=df_cols,
        index_col=index_col)


def read_csv(dropbox_path: str, csv_read_config: object) -> pd.DataFrame:
    '''
    Read CSV from a url
    ARGS:
        dropbox_path: Path to the file to be read
        csv_read_config: File configurations for reading the csv file
    '''
    buffer = dropbox_to_buffer(dropbox_path)
    df = read_csv_from_buffer(buffer, csv_read_config)
    return df


def read_csv_from_buffer(buffer: io.BytesIO, csv_read_config: object) -> pd.DataFrame:
    '''
    Read CSV from a bytes io instance
    ARGS:
        bytes_io: A bytes IO instance
        csv_read_config: File configurations for reading the csv file
    RETURNS:
        df: Resulting pandas dataframe
    '''
    seperator = csv_read_config.seperator
    df = pd.read_csv(buffer, sep=seperator)
    df.columns = df.columns.astype('str')
    df.columns = df.columns.str.upper()
    expected_cols = csv_read_config.expected_cols
    df_cols = csv_read_config.df_cols

    if expected_cols is not None:
        validate_columns(df, expected_cols)
        df = df[expected_cols]
    if df_cols is not None:
        df = df.rename(columns=dict(zip(df.columns, df_cols)))
    if csv_read_config.index_col is not None:
        df = df.set_index(csv_read_config.index_col)

    return df


# Excel

def make_excel_config(
        sheet_name: str = 'Sheet1',
        header: int = 0,
        expected_cols: List = None,
        df_cols: List = None,
        index_col: str = None) -> object:
    '''Excel config constructor'''
    ExcelReadConfig = namedtuple(
        'ExcelReadConfig',
        [
            'sheet_name',
            'header',
            'expected_cols',
            'df_cols',
            'index_col',
        ]
    )
    return ExcelReadConfig(
        sheet_name=sheet_name,
        header=header,
        expected_cols=expected_cols,
        df_cols=df_cols,
        index_col=index_col)


def read_excel(dropbox_path: str, excel_read_config: object) -> pd.DataFrame:
    '''
    Read Excel from dropbox path
    ARGS:
        dropbox_path: Path to file on dropbox
        excel_read_config: Configurations for reading excel files
    RETURNS:
        df: Resulting dataframe
    '''
    buffer = dropbox_to_buffer(dropbox_path)
    df = read_excel_from_buffer(buffer, excel_read_config)
    return df


def read_excel_from_buffer(buffer: io.BytesIO, excel_read_config: object) -> pd.DataFrame:
    '''
    Read excel from a bytes io instance
    ARGS:
        bytes_io: Instance of bytes io to read excel dataframe from
        excel_read_config: File configurations for reading the excel file
    RETURNS:
        df: Resulting dataframe
    '''
    sheet_name = excel_read_config.sheet_name
    header = excel_read_config.header
    df = pd.read_excel(buffer, sheet_name=sheet_name, header=header)
    df.columns = df.columns.astype('str')
    df.columns = df.columns.str.upper()
    expected_cols = excel_read_config.expected_cols
    df_cols = excel_read_config.df_cols

    if expected_cols is not None:
        validate_columns(df, expected_cols)
        df = df[expected_cols]
    if df_cols is not None:
        df = df.rename(columns=dict(zip(df.columns, df_cols)))
    if excel_read_config.index_col is not None:
        df = df.set_index(excel_read_config.index_col)

    return df


# Validation

def validate_columns(df: pd.DataFrame, expected_columns: List):
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

def dropbox_to_buffer(dropbox_path: str, read_timeout: int = 10) -> io.BytesIO:
    '''
    Download a file from dropbox and read into a buffer
    ARGS:
        dropbox_path: Path to file on dropbox to be read
        timeout: Time to wait for for reading IO data
    RETURNS:
        buffer: BytesIO instance of the file read from dropbox
    '''
    try:
        url = make_file_link(dropbox_path)
        buffer = io.BytesIO(requests.get(url, timout=read_timeout).content)
    except requests.exceptions.RequestException as err:
        raise exceptions.FileDownloadException(err)

    return buffer


def make_file_link(dropbox_path: str, max_tries: int = 5) -> str:
    '''
    Creates file link for a path on dropbox. The function
    tries to generate link and retries a few times before
    throwing an exception
    ARGS:
        dropbox_path: Path to file on dropbox
        max_tries: Number of tries before failing
    RETURNS:
        link: Temporary url to the file
    '''
    tries_count = 0
    while True:
        try:
            tries_count += 1
            link = core.make_file_link(dropbox_path)
            return link
        except exceptions.DropboxException as err:
            LOGGER.warning(err)
            if tries_count >= max_tries:
                raise
        else:
            break
