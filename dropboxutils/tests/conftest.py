'''Configurations for all tests'''

import os
import pytest
import dropbox


@pytest.fixture(scope='session')
def client():
    token = os.environ.get('DROPBOX_API_TOKEN')
    return dropbox.Dropbox(token)


@pytest.fixture(scope='session')
def test_directory(client):
    dirpath = '/ai/test'
    client.files_create_folder_v2(dirpath)
    yield dirpath
    client.files_delete_v2(dirpath)
