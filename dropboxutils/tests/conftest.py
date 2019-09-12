'''Configurations for all tests'''

import os
import pytest
import dropbox

from .. import files


@pytest.fixture(scope='session')
def client():
    token = os.environ.get('DROPBOX_API_TOKEN')
    return dropbox.Dropbox(token)


@pytest.fixture(scope='session')
def test_directory(client):
    dirpath = '/ai/test'

    if not files.exists(dirpath):
        client.files_create_folder_v2(dirpath)

    yield dirpath
    client.files_delete_v2(dirpath)
