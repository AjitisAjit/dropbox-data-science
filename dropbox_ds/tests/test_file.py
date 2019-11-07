'''
test_files
--------------
'''
import datetime
import posixpath

import pytest
import pandas as pd

from .. import file


# A factory for fixture types


@pytest.fixture(scope='function')
def csv_config():
    return file.CsvConfig(
        header=0,
        cols=list(range(4)),
        col_names={'Unnamed: 0': 'index', 'a': 'a', 'b': 'b', 'c': 'c'},  # Same as original
        index_col_name='index',
    )


@pytest.fixture(scope='function')
def excel_config():
    return [
        file.ExcelSheetConfig(
            sheet_name='sheet_1',
            header=0,
            index_col_name='index',
            cols=list(range(4)),
            col_names={'Unnamed: 0': 'index', 'a': 'a', 'b': 'b', 'c': 'c'},

        ),
        file.ExcelSheetConfig(
            sheet_name='sheet_2',
            header=0,
            cols=list(range(4)),
            index_col_name='index',
            col_names={'Unnamed: 0': 'index', 'd': 'd', 'e': 'e', 'f': 'f'},
        )
    ]


class TestDropboxFile:

    def test_upload(self, dropbox_file):
        text_data = dropbox_file('test.txt')
        text_payload = text_data['payload']
        text_file = text_data['file']
        text_file.upload(text_payload, timestamp=True)

    def test_download(self, dropbox_file, csv_config, excel_config):
        text_data = dropbox_file('test.txt')
        text_file = text_data['file']
        text_payload = text_data['payload']
        text_original = text_data['data']

        csv_data = dropbox_file('test.csv')
        csv_file = csv_data['file']
        csv_payload = csv_data['payload']
        csv_original = csv_data['data']

        excel_data = dropbox_file('test.xlsx')
        excel_file = excel_data['file']
        excel_payload = excel_data['payload']
        excel_original = excel_data['data']

        text_file.upload(text_payload)
        csv_file.upload(csv_payload)
        excel_file.upload(excel_payload)
        text_downloaded = text_file.download()
        csv_downloaded = csv_file.download(csv_config)

        excel_downloaded = excel_file.download(excel_config)
        first, second = excel_downloaded
        merged_df = first.merge(second, left_index=True, right_index=True, how='outer')

        assert merged_df.equals(excel_original)
        assert text_downloaded == text_original
        assert csv_downloaded.equals(csv_original)

    def test_move(self, dropbox_file):
        text_data = dropbox_file('test.txt')
        text_file = text_data['file']
        text_payload = text_data['payload']

        text_file.upload(text_payload)
        path = text_file.path
        new_path = posixpath.join(posixpath.dirname(path), 'test_2')
        text_file.move(new_path)
        assert text_file.path == new_path

    def test_copy(self, dropbox_file, api_token):
        text_data = dropbox_file('test.txt')
        text_file = text_data['file']
        text_payload = text_data['payload']

        text_file.upload(text_payload)
        path = text_file.path
        new_path = posixpath.join(posixpath.dirname(path), 'test_2')
        new_file = file.make_dropbox_file(new_path, api_token)

        text_file.copy(new_path)
        assert text_file.exists()
        assert new_file.exists()

    def test_get_props(self, dropbox_file):
        text_data = dropbox_file('test.txt')
        text_file = text_data['file']
        text_payload = text_data['payload']

        text_file.upload(text_payload)
        assert isinstance(text_file.path, str)
        assert isinstance(text_file.content_hash, str)
        assert isinstance(text_file.last_modified, datetime.datetime)
