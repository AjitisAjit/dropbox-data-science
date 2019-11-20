'''Configurations for all tests'''

import os
import io
import pytest
import posixpath
from typing import Callable, Dict
import dropbox

import pandas as pd
from .. import dropboxfolder, dropboxfile


@pytest.fixture(scope='session')
def api_token():
    return os.environ.get('DROPBOX_API_TOKEN')


@pytest.fixture(scope='session')
def client(api_token):
    return dropbox.Dropbox(api_token)


@pytest.fixture(scope='function')
def folder_instance(api_token):
    dirpath = '/ai/test'
    folder_obj = dropboxfolder.DropboxFolder(dirpath, api_token)
    folder_obj.create()
    yield folder_obj
    folder_obj.delete()


# File factory

@pytest.fixture(scope='function')
def dropbox_file(folder_instance, api_token) -> Callable:

    def make_dropbox_file(filename) -> Dict:
        path = posixpath.join(folder_instance.path, filename)
        file_instance = dropboxfile.make_dropbox_file(path)

        if isinstance(file_instance, dropboxfile.DropboxTextFile):
            original_data = 'This is text data'
            bytes_data = bytes(original_data, encoding='utf8')

        elif isinstance(file_instance, dropboxfile.DropboxCsvFile):
            original_data = pd.DataFrame({
                'a': [1, 2, 3],
                'b': [4, 5, 6],
                'c': [7, 8, 9]
            })

            io_instance = io.StringIO()
            original_data.to_csv(io_instance)
            bytes_data = bytes(io_instance.getvalue(), encoding='utf8')

        elif isinstance(file_instance, dropboxfile.DropboxExcelFile):
            sheet_1 = pd.DataFrame({
                'a': [1, 2, 3],
                'b': [4, 5, 6],
                'c': [7, 8, 9]
            })
            sheet_2 = pd.DataFrame({
                'd': [10, 11, 12],
                'e': [13, 14, 15],
                'f': [16, 17, 18]
            })

            io_instance = io.BytesIO()

            with pd.ExcelWriter(io_instance) as writer:
                sheet_1.to_excel(writer, sheet_name='sheet_1')
                sheet_2.to_excel(writer, sheet_name='sheet_2')

            original_data = sheet_1.merge(sheet_2, how='outer', left_index=True, right_index=True)
            bytes_data = io_instance.getvalue()

        return {'file': file_instance, 'data': original_data, 'payload': bytes_data}

    yield make_dropbox_file
