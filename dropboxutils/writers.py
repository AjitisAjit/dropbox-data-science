'''
Writers provide functionality for writing various files.
These include
- CSV
- Excel
'''

import  io
import time
import logging
from typing import List, Dict
from collections import namedtuple

import yaml
import pandas as pd
from . import core, exceptions


LOGGER = logging.getLogger('dropboxutils')


# CSV

def make_csv_write_config(
        sep=',',
        encoding='utf8'
):
    '''CSV config constructor'''
    CSVWriteConfig = namedtuple(
        'ExcelReadConfig',
        [
            'sep',
            'encoding'
        ]
    )
    return CSVWriteConfig(
        sep=sep,
        encoding=encoding
    )


def write_csv(df, dropbox_path: str, index=False):
    '''
    Writes csv file to dropbox. The files are written in utf8 encoding
    ARGS:
        df: Dataframe to be written to csv
        dropbox_path: Path on dropbox to write file to
        write_config: A configuration object that defines how files are written
    '''
    encoding = 'utf8'
    LOGGER.debug('Writing csv file to buffer')
    buffer = csv_to_buffer(df, index=index)
    bytes_data = bytes(buffer.getvalue(), encoding)
    LOGGER.debug('Uploading csv data to dropbox')
    bytes_to_dropbox(bytes_data, dropbox_path)


def csv_to_buffer(df: pd.DataFrame, index=False) -> io.StringIO:
    '''
    Writes csv data to a StringIO instance. Note that csv files
    are written with ',' acting as seperator and utf8 encoding
    ARGS:
        df: Dataframe to be written to StringIO buffer
        write_config: Configuration with parameters for writing csv
    RETURNS:
        buffer: StringIO instance to which the data is written
    '''
    sep = ','
    buffer = io.StringIO()
    df.to_csv(buffer, sep=sep, index=index)
    return buffer


# Excel

def write_excel(df_list: List[pd.DataFrame], dropbox_path: str, index: bool = False, style_yaml: str = None):
    '''
    Write excel file to Dropbox path. An excel file can contain
    multiple sheets, each of the sheets could have different
    styles associations
    ARGS:
        df_list: List of dataframes to be written
        dropbox_path: Path on dropbox to for the excel file to be saved
        index: Whether to include dataframe index in the excel output
        style_yaml: A yaml file containing formatting information for each sheet in file
    '''
    if style_yaml is not None:
        style_config = parse_style_yaml(style_yaml)
    else:
        style_config = None

    LOGGER.debug('Writing Excel file to buffer')
    buffer = excel_to_buffer(df_list, style_config=style_config, index=index)
    bytes_data = buffer.getvalue()
    LOGGER.debug('Uploading excel data to dropbox')
    bytes_to_dropbox(bytes_data, dropbox_path)


def parse_style_yaml(path) -> List[Dict]:
    '''
    Reads and parses yaml file to generate format dictionaries
    for each sheet in the excel file
    ARGS:
        path: Path to yaml file to be read
    RETURNS:
        sheets: Formatting configurations for each sheet
    '''
    try:
        with open(path, 'rt') as yaml_fd:
            sheets = list(yaml.load_all(yaml_fd))
    except IOError as err:
        raise exceptions.ReaderException(err)
    return sheets


def excel_to_buffer(df: pd.DataFrame, style_config: object = None, index: bool = None) -> io.BytesIO:
    pass


# Common

def bytes_to_dropbox(bytes_data: bytes, dropbox_path: str, max_tries: int = 5):
    tries_count = 0
    while True:
        try:
            tries_count += 1
            core.upload_to_dropbox(bytes_data, dropbox_path)
        except exceptions.DropboxException as err:
            LOGGER.warning(err)
            time.sleep(1)
            if tries_count >= max_tries:
                raise exceptions.FileUploadException(err)
        else:
            break
