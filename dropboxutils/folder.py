'''
Defines the class for managing folders and maintaining their
state
'''

import os
from typing import Optional, List, Tuple

import dropbox

from .file import make_dropbox_file
from .exceptions import DropboxFolderError


class DropboxFolder:
    '''
    Attributes:
        flist: List of files and folders in the dropbox folder
        cursor: Dropbox cursor associated with the folder

    Methods:
        create: Creates an empty folder with the name
        update: Refresh the state of the folder
        delete: Deletes the folder
    '''

    def __init__(self, folder: str, api_token: Optional[str] = None):
        self._api_token = api_token if api_token is not None else os.environ.get('DROPBOX_API_TOKEN')
        self._client = dropbox.Dropbox(self._api_token)
        self._folder = folder.path_lower if isinstance(folder, dropbox.files.FileMetadata) else folder
        self._cursor = None
        self._flist = None

    @property
    def path(self):
        return self._folder

    @property
    def cursor(self):
        return self._cursor

    @property
    def flist(self):
        return self._flist

    def create(self) -> None:
        try:
            self._client.files_create_folder_v2(self._folder)
        except Exception as err:
            raise DropboxFolderError(err)

    def update(self) -> None:
        if self._cursor is None and self._flist is None:
            self._cursor, self._flist = self._get_changes_from_path()
        else:
            cursor, changes = self._get_changes_from_cursor()
            total_files = list(set(self._flist).union(changes))
            self._flist = total_files
            self._cursor = cursor

    def delete(self) -> None:
        try:
            self._client.files_delete_v2(self._folder)
        except Exception as err:
            raise DropboxFolderError(err)

    def _get_changes_from_cursor(self) -> Tuple[str, List]:
        try:
            result = self._client.files_list_folder_continue(self._cursor)
        except Exception as err:
            raise DropboxFolderError(err)

        files = self._get_files(result.entries)
        return result.cursor, files

    def _get_changes_from_path(self) -> Tuple[str, List]:
        try:
            contents = self._client.files_list_folder(self._folder)
        except Exception as err:
            raise DropboxFolderError(err)

        files = self._get_files(contents.entries)
        return contents.cursor, files

    def _get_files(self, files: List) -> List:
        return [make_dropbox_file(f, self._api_token) for f in files if isinstance(f, dropbox.files.FileMetadata)]
