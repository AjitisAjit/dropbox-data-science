'''
file.py
-------

File operations on dropbox
'''

import re
import os
import io
import hashlib
import datetime
import posixpath
from dataclasses import dataclass
from typing import Optional, NewType, Union, List, Dict

import dropbox
import requests
import pandas as pd

from .exceptions import DropboxFileError


# Constants

TIME_FORMAT = '%Y%m%d_%H:%M'


# Dataclasses

@dataclass
class ExcelSheetConfig:
    sheet_name: str = 'Sheet1'
    header: int = 0
    cols: Optional[List[int]] = None
    col_names: Optional[Dict] = None
    index_col_name: Optional[str] = None


@dataclass
class CsvConfig:
    header: int = 0
    col_names: Optional[Dict] = None
    cols: Optional[List[int]] = None
    index_col_name: Optional[str] = None


DateTime = NewType('datetime.datetime', object)

ReadConfig = Union[List[ExcelSheetConfig], CsvConfig]

WriteMode = dropbox.files.WriteMode('overwrite')  # Files are always overwritten on dropbox


class Base:
    '''
    Attributes:
        path: Path to the file on dropbox
        content_hash: Hash of the content of file
        last_modified: Datetime when the file was last modified/Added

    Methods:
        exists: Check if the file exists
        upload: Upload data to file (Overwrite)
        download: Downloads the contents of bath to bytes
        move: Moves path to a destination file path
        copy: Self explanatory
        delete: Remove the file from dropbox folder

    Base class for all dropbox file instances
    '''

    def __init__(
            self,
            path: str,
            client: dropbox.Dropbox,
            last_modified: Optional[datetime.datetime] = None,
            content_hash: Optional[str] = None,
    ):
        self._path = path
        self._client = client
        self._last_modified = last_modified
        self._content_hash = content_hash

    def __eq__(self, other):
        return self.path == other.path

    def __lt__(self, other):
        return self.path < other.path

    def __hash__(self):
        return int(hashlib.md5(self._path.encode('utf8')).hexdigest(), 16)

    def __repr__(self):
        return '{class_name}(path={path}, last_modified={last_modified}, content_hash={content_hash})'.format(
            class_name=self.__class__.__name__,
            path=self._path,
            last_modified=self._last_modified,
            content_hash=self._content_hash
        )

    @property
    def path(self) -> str:
        '''
        Full filepath in lowercase
        '''
        return self._path

    @property
    def last_modified(self) -> DateTime:
        '''
        Last edited by the client
        '''
        if self._last_modified is None:
            self.update_metadata()
        return self._last_modified

    @property
    def content_hash(self):
        '''
        Hash of the file contents sha256
        '''
        if self._content_hash is None:
            self.update_metadata()
        return self._content_hash

    def exists(self) -> bool:
        '''
        RETURNS:
            bool value indicating if file exists

        Check whether the file exits on dropbox
        '''
        try:
            self.update_metadata()
            return True
        except Exception as err:
            if isinstance(err, dropbox.exceptions.ApiError) and\
               isinstance(err.error, dropbox.files.GetMetadataError) and\
               isinstance(err.error.get_path, LookupError):  # File doesn't exist
                return False
            else:
                raise DropboxFileError(err)

    def upload(self, data: bytes, timestamp: bool = False):
        '''
        ARGS:
            data: bytes to be uploaded to path
            timestamp: boolean indicating whether to attach timestamp to uploaded file

        Uploads data in bytes to a filepath
        '''
        if timestamp is True:
            filename = datetime.datetime.utcnow().strftime(TIME_FORMAT) + posixpath.basename(self._path)
            self._path = posixpath.join(posixpath.dirname(self._path), filename)

        try:
            self._client.files_upload(data, self._path, mode=WriteMode)
            self.update_metadata()
        except Exception as err:
            raise DropboxFileError(err)

    def download(self) -> bytes:
        '''
        RETURNS:
            Data in bytes

        Download data in bytes from path on dropbox
        '''
        try:
            link = self._client.files_get_temporary_link(self._path).link
            return requests.get(link).content
        except Exception as err:
            raise DropboxFileError(err)

    def move(self, dest: str) -> None:
        '''
        ARGS:
            dest: Destination path as string

        Move file to destination path
        '''
        try:
            self._client.files_move_v2(self._path, dest)
            self.update_metadata(path=dest)
        except Exception as err:
            DropboxFileError(err)

    def copy(self, dest: str) -> None:
        '''
        ARGS:
            dest: Destination full path

        Create a copy of the file at destination. File path remains unchanged
        '''
        try:
            self._client.files_copy_v2(self._path, dest)
        except Exception as err:
            DropboxFileError(err)

    def delete(self):
        '''
        Delete file from dropbox
        '''
        try:
            self._client.files_delete_v2(self._path)
        except Exception as err:
            DropboxFileError(err)

    def update_metadata(self, path=None):
        '''
        ARGS:
           path: (optional) new path to file

        Update metadata properties of the file. If the path is set,
        it is considered as filepath
        '''
        try:
            self._path = path if path is not None else self._path
            metadata = self._client.files_get_metadata(self._path)
            self._path = metadata.path_lower
            self._last_modified = metadata.client_modified
            self._content_hash = metadata.content_hash
        except Exception as err:
            raise DropboxFileError(err)


class DropboxTextFile(Base):
    '''
    Text file as encoding string desribed by attribute
    '''

    def __init__(self, *args, encoding: str = 'utf8', **kwargs):
        self._encoding = encoding
        super().__init__(*args, **kwargs)

    def download(self) -> str:
        '''
        Returns the string with set encoding
        '''
        data = super().download()
        return data.decode(self._encoding)


class DropboxCsvFile(Base):
    '''
    Csv file as dataframe with utf-8 encoded text
    '''

    def __init__(self, *args, encoding: str = 'utf8', **kwargs):
        self._encoding = encoding
        super().__init__(*args, *kwargs)

    def download(self, csv_config: CsvConfig) -> pd.DataFrame:
        '''
        ARGS:
            csv_config: Instance of CsvConfig containing table information

        Returns a pandas dataframe with set encoding
        '''
        data = super().download()
        buffer = io.StringIO(data.decode(self._encoding))
        return self._read_file(buffer, csv_config)

    @staticmethod
    def _read_file(buffer, config: CsvConfig) -> pd.DataFrame:
        df = pd.read_csv(buffer, header=config.header, usecols=config.cols)

        if config.col_names:
            assert sorted(df.columns) == sorted(config.col_names.keys())
            df = df.rename(columns=config.col_names)

        df = df.set_index(config.index_col_name) if config.index_col_name else df
        return df


class DropboxExcelFile(Base):
    '''
    Excel file as a list of dataframes
    '''

    def download(self, sheet_config_list: List[ExcelSheetConfig]) -> List[pd.DataFrame]:
        '''
        ARGS:
            sheet_config_list: List of Excel sheet config instances

        Returns a list of dataframes for each sheet
        '''
        data = super().download()
        buffer = io.BytesIO(data)
        return list(map(lambda c: self._read_sheet(buffer, c), sheet_config_list))

    @staticmethod
    def _read_sheet(buffer, config: ExcelSheetConfig) -> pd.DataFrame:
        df = pd.read_excel(buffer, config.sheet_name, header=config.header, usecols=config.cols)

        if config.col_names:
            assert sorted(df.columns) == sorted(config.col_names.keys())
            df = df.rename(columns=config.col_names)

        df = df.set_index(config.index_col_name) if config.index_col_name else df
        return df


# File Factory

File = Union[DropboxExcelFile, DropboxCsvFile, DropboxTextFile]


def make_dropbox_file(file: Union[str, dropbox.files.FileMetadata], api_token: Optional[str] = None) -> File:
    '''
    ARGS:
        file: A metadata object or filepath
        api_token: Dropbox API token

    Create an instance of dropbox file
    '''
    client = dropbox.Dropbox(os.environ.get('DROPBOX_API_TOKEN')) if api_token is None else dropbox.Dropbox(api_token)

    pattern_to_filetype = [
        (DropboxExcelFile, r'^.+\.xlsx?$'),
        (DropboxCsvFile,   r'^.+\.csv$'),
        (DropboxTextFile,  r'^.+$')
    ]

    if isinstance(file, dropbox.files.FileMetadata):
        path = file.path_lower
        last_modified = file.client_modified
        content_hash = file.content_hash
        instance = next(Class(path, client, last_modified=last_modified, content_hash=content_hash)
                        for Class, regex in pattern_to_filetype if re.match(regex, path))
    else:
        instance = next(Class(file, client) for Class, regex in pattern_to_filetype if re.match(regex, file))

    return instance
