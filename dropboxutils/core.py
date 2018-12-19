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

# Rename path

# List files

def make_file_link(path: str) -> str:
    '''
    Make temporary file link for getting files
    from dropbox
    ARGS:
        dropbox_path: Path to file on dropbox
    RETURNS:
        file_link: Temporary file link
    '''
    try:
        file_link = CLIENT.files_get_temporary_link(path).link
    except (requests.exceptions.RequestException, dropbox.exceptions.DropboxException) as err:
        raise exceptions.DropboxException(err)
    return file_link
