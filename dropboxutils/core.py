'''
Core utilities used by dropbox. To create a dropbox client
define an environment variable `DROPBOX_API_TOKEN` with
dropbox api key
'''

import os
import requests
import dropbox

from . import exceptions


TOKEN = os.environ.get('DROPBOX_API_TOKEN')

CLIENT = dropbox.Dropbox(TOKEN)


def make_file_link(path: str) -> str:
    '''
    Make temporary file link for getting files
    from dropbox
    ARGS:
        path: Path to file on dropbox
    RETURNS:
        file_link: Temporary file link
    '''
    try:
        file_link = CLIENT.files_get_temporary_link(path).link
    except (requests.exceptions.RequestException, dropbox.exceptions.DropboxException) as err:
        raise exceptions.DropboxException(err)
    return file_link


def upload_to_dropbox(data: bytes, path: str, write_mode=dropbox.files.WriteMode('overwrite')):
    '''
    Upload bytes data to a path on dropbox
    ARGS:
        data: The data in bytes to be uploaded to dropbox
        path: Path to which the data is to be uploaded
        write_mode: Determines whether overwritting an existing file is permitted
    '''
    try:
        CLIENT.files_upload(data, path, write_mode)
    except (dropbox.exceptions.DropboxException, requests.exceptions.RequestException) as err:
        raise exceptions.DropboxException(err)


def list_files_shallow(path: str):
    '''
    List contents of a folder.
    ARGS:
        path: Path on dropbox to be listed
    '''
    try:
        flist = CLIENT.files_list_folder(path)
    except (dropbox.exceptions.DropboxException, requests.exceptions.RequestException)  as err:
        raise exceptions.DropboxException('An error occurred getting file contents - {}'.format(err))
    return flist
