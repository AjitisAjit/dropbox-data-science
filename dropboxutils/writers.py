'''
Writers provide functionality for writing various files.
These include
- CSV
- Excel
'''

import  io
import logging

import pandas as pd
from . import core, exceptions


LOGGER = logging.getLogger('dropboxutils')


# CSV

def write_csv(
        df,
        dropbox_path: str,
        sep: str = ',',
        index: bool = False,
        encoding: str = 'UTF-8'
):
    LOGGER.debug('Writing csv file to buffer')
    buffer = csv_to_buffer(df, sep=sep, index=index)
    bytes_data = bytes(buffer.getvalue().decode(encoding))
    LOGGER.debug('Uploading csv data to dropbox')
    bytes_to_dropbox(bytes_data, dropbox_path)


def csv_to_buffer(df: pd.DataFrame, sep: str = ',', index: bool = False) -> io.StringIO:
    buffer = io.StringIO()
    df.to_csv(buffer, sep=sep, index=index)
    return buffer


# Excel

def write_excel(
        df,
        dropbox_path: str,
        format_path: str,
        use_index: bool = False
):
    format_config = parse_format_yaml(format_filepath)
    LOGGER.debug('Writing Excel file to buffer')
    buffer = excel_to_buffer(df, format_config, use_index=use_index)
    bytes_data = bytes(buffer.getvalue())
    LOGGER.debug('Uploading excel data to dropbox')
    bytes_to_dropbox(bytes_data, dropbox_path)


def excel_to_buffer(df, format_config: object, use_index=False):
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
            if tries_count >= max_tries:
                raise exceptions.FileUploadException(err)
        else:
            break
