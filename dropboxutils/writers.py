'''
Writers provide functionality for writing various files
These include
- CSV
- Excel
'''

import  io
import time
import logging
from typing import List, Dict
from collections import namedtuple

import xlsxwriter
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
    validate_df(df)
    sep = ','
    buffer = io.StringIO()
    df.to_csv(buffer, sep=sep, index=index)
    return buffer


# Excel

def write_excel(df_list: List[pd.DataFrame], dropbox_path: str, configfile: str):
    '''
    Write excel file to Dropbox path. An excel file can contain
    multiple sheets, each of the sheets could have different
    styles associations
    ARGS:
        df_list: List of dataframes to be written
        dropbox_path: Path on dropbox to for the excel file to be saved
        index: Whether to include dataframe index in the excel output
        configfile: A yaml file containing formatting information for each sheet in file
    '''
    LOGGER.debug('Writing Excel file to buffer')
    config_list = parse_yaml(configfile)
    buffer = excel_to_buffer(df_list, config_list)
    bytes_data = buffer.getvalue()
    LOGGER.debug('Uploading excel data to dropbox')
    bytes_to_dropbox(bytes_data, dropbox_path)


def excel_to_buffer(df_list: List[pd.DataFrame], config_list: List[Dict]) -> io.BytesIO:
    '''
    Reads excel data into a buffer
    ARGS:
        df_list: List of dataframes to be written to excel file
        configfile: File containing configurations data
    '''
    import pandas.io.formats.excel
    pandas.io.formats.excel.header_style = None # Ignores header format

    validate_excel(df_list, config_list)
    buffer = io.BytesIO()
    writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
    workbook = writer.book

    for df, sheet_config in zip(df_list, config_list):
        sheet_name = sheet_config['sheet']
        df.to_excel(writer, sheet_name=sheet_name, index=sheet_config['index'])
        df_to_sheet(sheet_config, workbook, writer)

    writer.save()
    buffer.seek(0)
    return buffer


def validate_excel(df_list: List[pd.DataFrame], config: List[Dict]):
    '''
    Validates the dataframes and configurations for
    writing to excel
    '''
    try:
        assert len(df_list) == len(config)
        map(validate_df, df_list)
    except AssertionError as err:
        raise exceptions.WriterException(err)


def df_to_sheet(sheet_config: Dict, workbook: xlsxwriter.Workbook, writer: pd.ExcelWriter):
    '''
    Write dataframe to excel sheet in the buffer
    '''
    sheet_name = sheet_config['sheet']
    worksheet = writer.sheets[sheet_name]
    rows = sheet_config['rows']
    cols = sheet_config['columns']
    set_sheet_rows(rows, workbook, worksheet)
    set_sheet_cols(cols, workbook, worksheet)

    worksheet.set_zoom(sheet_config['zoom'])
    if sheet_config.get('frozen_panes', None):
        frozen_panes_str = sheet_config.get('frozen_panes')
        frozen_panes = list(map(int, frozen_panes_str.split(','))) #TODO: Find a better solution
        worksheet.freeze_panes(*frozen_panes)

    return writer


def set_sheet_rows(row_dict, book, sheet):
    '''
    Formats rows in an excel sheet based on formatting
    information
    ARGS:
        row_dict: A dictionary containing formatting information
        book: Workbook object associated with xslxwriter
        sheet: Excel sheet containing rows to be formatted
    '''
    for row_range_str, fmt in row_dict.items():
        style_dict = fmt['style']
        style_fmt = book.add_format(style_dict)

        if fmt.get('align', None) and fmt.get('align'):
            style_fmt.set_align('center')
            style_fmt.set_align('vcenter')

        height = fmt['height']
        row_range = make_range(row_range_str)
        for row_idx in row_range:
            sheet.set_row(row_idx, height, style_fmt)


def set_sheet_cols(col_dict, book, sheet):
    '''
    Formats columns in an excel sheet based on formatting
    information
    ARGS:
        col_dict: A dictionary containing formatting information
        book: Workbook object associated with xlsxwriter
        sheet: Excel sheet containing columns to be formatted
    '''
    for col_range_str, fmt in col_dict.items():
        style_dict = fmt['style']
        style_fmt = book.add_format(style_dict)

        if fmt.get('align', None) and fmt.get('align'):
            style_fmt.set_align('center')
            style_fmt.set_align('vcenter')

        width = fmt['width']
        col_range = make_range(col_range_str)
        for col_idx in col_range:
            sheet.set_row(col_idx, width, style_fmt)


def parse_yaml(path) -> List[Dict]:
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
    except (FileNotFoundError, yaml.YAMLError) as err:
        raise exceptions.ReaderException(err)
    return sheets


# Common

def make_range(range_str: str) -> range:
    '''
    Create a range from string its string representation
    . The string representation of range is similar to
    list slicing in python. The only difference being that
    both first and last index are considered in range
    EG:
        "3:4" => range(3, 5) [Includes 3 and 4]
    ARGS:
        range_str: A string representation of range
    '''
    try:
        range_list = list(map(int, range_str.split(':')))
        assert len(range_list) in  [1, 2]
        start = range_list[0]
        end = start + 1 if len(range_list) == 1 else range_list[1] + 1
        return range(start, end)
    except (AssertionError, ValueError) as err:
        raise exceptions.ReaderException('Error parsing range - {} - {}'.format(range_str, err))


def validate_df(df: pd.DataFrame):
    '''
    Asserts if the dataframe is  valid
    ARGS:
        df: Dataframe to be checked
    '''
    try:
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
    except AssertionError as err:
        raise exceptions.WriterException(err)


def bytes_to_dropbox(bytes_data: bytes, dropbox_path: str, max_tries: int = 5):
    '''
    Tries to upload bytes to a file on dropbox. If the upload fails, the program retries
    a number of times before raising an exception
    '''
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
