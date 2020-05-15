'''
Defines the class for managing folders and maintaining their
state
'''

import os
import hashlib
import posixpath
from typing import Optional, List, Tuple

import dropbox

from .dropboxfile import make_dropbox_file
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
        self._api_token = api_token if api_token is not None else os.environ.get(
            'DROPBOX_API_TOKEN')
        self._client = dropbox.Dropbox(self._api_token)
        self._path = folder.path_lower if isinstance(
            folder, dropbox.files.FileMetadata) else folder
        self._cursor = ''
        self._flist = []

    def __hash__(self):
        return int(hashlib.md5(self._path.encode('utf8')).hexdigest(), 16)

    def __eq__(self, other):
        return self._path == other.path

    def __repr__(self):
        return 'DropboxFolder({name}: [{flist}])'.format(
            name=self._path,
            flist=','.join([str(f) for f in self._flist])
        )

    @property
    def path(self):
        '''
        Lowercase full path to file
        '''
        return self._path

    @property
    def cursor(self):
        '''
        A String cursor representing folder state
        '''
        return self._cursor

    @property
    def flist(self):
        '''
        List of files in folder
        '''
        return self._flist

    def create(self) -> None:
        '''
        Creates a new folder with given path
        '''
        try:
            self._client.files_create_folder_v2(self._path)
        except Exception as err:
            raise DropboxFolderError(err)

    def update(self) -> None:
        '''
        Updates the state of the given folder. Including
        cursor and file list
        '''
        cursor, changes = self._get_changes_from_path(
        ) if self._cursor == '' else self._get_changes_from_cursor()
        flist = self._get_files(changes)
        self._flist = flist
        self._cursor = cursor

    def delete(self) -> None:
        '''
        Deletes the folder with path
        '''
        try:
            self._client.files_delete_v2(self._path)
        except Exception as err:
            raise DropboxFolderError(err)

    def _get_changes_from_cursor(self) -> Tuple[str, List]:
        try:
            result = self._client.files_list_folder_continue(self._cursor)
        except Exception as err:
            raise DropboxFolderError(err)

        flist = []

        def process_entries(entries):
            for e in entries:
                flist.append(e)

        process_entries(result.entries)

        while result.has_more:
            try:
                result = self._client.files_list_folder_continue(result.cursor)
            except Exception as err:
                raise DropboxFolderError(err)

            process_entries(result.entries)

        return result.cursor, flist

    def _get_changes_from_path(self) -> Tuple[str, List]:
        try:
            result = self._client.files_list_folder(self._path)
        except Exception as err:
            raise DropboxFolderError(err)

        flist = []

        def process_entries(entries):
            for e in entries:
                flist.append(e)

        process_entries(result.entries)

        while result.has_more:
            try:
                result = self._client.files_list_folder_continue(result.cursor)
            except Exception as err:
                raise DropboxFolderError(err)

            process_entries(result.entries)

        return result.cursor, flist

    def _get_files(self, folder_content: List) -> List:
        # Folders and Moved or deleted files are ignored. Files within subfolders are also ignored
        files = [f for f in folder_content if isinstance(f, dropbox.files.FileMetadata)]

        deleted_paths = [f.path_lower for
                         f in folder_content if isinstance(f, dropbox.files.DeletedMetadata)]

        files_added_or_modified = [make_dropbox_file(f, self._api_token) for
                                   f in files if self._path == posixpath.dirname(f.path_lower)]
        files_unchanged = [f for
                           f in self._flist
                           if f.path not in deleted_paths and
                           posixpath.dirname(f.path) == self.path]

        return list(set(files_unchanged).union(files_added_or_modified))
