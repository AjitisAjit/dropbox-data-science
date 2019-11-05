'''
file.py
-------

File operations on dropbox
'''

import re
import os
import io
import hashlib
import posixpath
from functools import reduce
from dataclasses import dataclass
from typing import Optional, NewType, Union, List, Dict

import dropbox
import requests
import pandas as pd

from .exceptions import DropboxFileError


DateTime = NewType('datetime.datetime', object)

WriteMode = dropbox.files.WriteMode('overwrite')  # Files are always overwritten on dropbox


# Dataclasses

@dataclass
class ExcelSheetConfig:
    sheet_name: str
    header: int
    col_names: Optional[Dict]
    cols: Optional[List[int]]
    index_col_name: Optional[str]


@dataclass
class CsvConfig:
    header: int
    col_names: Optional[Dict]
    cols: Optional[List[int]]
    index_col_name: Optional[str]


# FileFactory

def make_dropbox_file(file: Union[str, dropbox.files.FileMetadata], api_token: Optional[str] = None):
    client = dropbox.Dropbox(os.environ.get('DROPBOX_API_TOKEN')) if api_token is None else dropbox.Dropbox(api_token)
    path = file.path_lower if isinstance(file, dropbox.files.FileMetadata) else file

    excel_file_pattern = r'^.+\.xlsx?$'
    csv_file_pattern = r'^.+\.csv$'

    if re.match(excel_file_pattern, posixpath.basename(path)):
        return DropboxExcelFile(path, client)
        pass
    elif re.match(csv_file_pattern, posixpath.basename(path)):
        return DropboxCsvFile(path, client)
    else:
        return DropboxTextFile(path, client)


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

    def __init__(self, file: str, client: dropbox.Dropbox):
        self._file = file
        self._client = client

    def __eq__(self, other):
        return self.path == other.path

    def __lt__(self, other):
        return self.path < other.path

    def __hash__(self):
        return int(hashlib.md5(self._file.encode('utf8')).hexdigest(), 16)

    def __repr__(self):
        return '{class_name}(path={path}, last_modified={last_modified}, content_hash={content_hash})'.format(
            class_name=self.__class__.__name__,
            path=self.path,
            last_modified=self.last_modified,
            content_hash=self.content_hash
        )

    @property
    def path(self) -> str:
        return self._file

    @property
    def last_modified(self) -> DateTime:
        try:
            return self._get_metadata().client_modified
        except Exception as err:
            raise DropboxFileError(err)

    @property
    def content_hash(self):
        try:
            return self._get_metadata().content_hash
        except Exception as err:
            raise DropboxFileError(err)

    def exists(self) -> bool:
        try:
            self._get_metadata()
            return True
        except Exception as err:
            if isinstance(err, dropbox.exceptions.ApiError) and\
               isinstance(err.error, dropbox.files.GetMetadataError) and\
               isinstance(err.error.get_path, LookupError):  # File doesn't exist
                return False
            else:
                raise DropboxFileError(err)

    def upload(self, data: bytes):
        try:
            self._client.files_upload(data, self._file, mode=WriteMode)
        except Exception as err:
            raise DropboxFileError(err)

    def download(self) -> bytes:
        try:
            link = self._client.files_get_temporary_link(self._file).link
            return requests.get(link).content
        except Exception as err:
            raise DropboxFileError(err)

    def move(self, dest: str) -> None:
        try:
            self._client.files_move_v2(self._file, dest)
            self._file = dest
        except Exception as err:
            DropboxFileError(err)

    def copy(self, dest: str) -> None:
        try:
            self._client.files_copy_v2(self._file, dest)
        except Exception as err:
            DropboxFileError(err)

    def delete(self):
        try:
            self._client.files_delete_v2(self._file)
        except Exception as err:
            DropboxFileError(err)

    def _get_metadata(self) -> dropbox.files.FileMetadata:
        try:
            return self._client.files_get_metadata(self._file)
        except Exception as err:
            raise DropboxFileError(err)


class DropboxTextFile(Base):

    def __init__(self, file: str, client: dropbox.Dropbox, encoding: str = 'utf8'):
        self._encoding = encoding
        super().__init__(file, client)

    def download(self):
        data = super().download()
        return data.decode(self._encoding)


class DropboxCsvFile(Base):
    def __init__(self, file: str, client: dropbox.Dropbox, encoding: str = 'utf8'):
        self._encoding = encoding
        super().__init__(file, client)

    def download(self, csv_config: CsvConfig) -> pd.DataFrame:
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

    def download(self, sheet_config_list: List[ExcelSheetConfig]) -> pd.DataFrame:
        data = super().download()
        buffer = io.BytesIO(data)
        df_map = map(lambda c: self._read_sheet(buffer, c), sheet_config_list)
        return reduce(lambda df1, df2: pd.merge(df1, df2, left_index=True, right_index=True), df_map)

    @staticmethod
    def _read_sheet(buffer, config: ExcelSheetConfig) -> pd.DataFrame:
        df = pd.read_excel(buffer, config.sheet_name, header=config.header, usecols=config.cols)

        if config.col_names:
            assert sorted(df.columns) == sorted(config.col_names.keys())
            df = df.rename(columns=config.col_names)

        df = df.set_index(config.index_col_name) if config.index_col_name else df
        return df
