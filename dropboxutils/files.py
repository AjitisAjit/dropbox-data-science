'''
file.py
-------

File operations on dropbox
'''

import os
import logging
import posixpath
from typing import List, Tuple

import requests
import dropbox

from . import exceptions


CLIENT = dropbox.Dropbox(os.environ.get('DROPBOX_API_TOKEN'))

LOGGER = logging.getLogger('dropboxutils')


def download(path: str) -> bytes:
    '''
    ARGS:
        path: absolute path to file on dropbox

    Downloads binary data from a dropbox path
    '''
    try:
        link = CLIENT.files_get_temporary_link(path).link
        return requests.get(link).content
    except Exception as err:
        raise exceptions.DropboxFileError(err)


def upload(data: bytes, path: str, write_mode=dropbox.files.WriteMode('overwrite')):
    '''
    ARGS:
        data: The data in bytes to be uploaded to dropbox
        path: Path to which the data is to be uploaded
        write_mode: Determines whether overwritting an existing file is permitted

    Upload bytes data to a path on dropbox
    '''
    try:
        CLIENT.files_upload(data, path, write_mode)
    except Exception as err:
        raise exceptions.DropboxFileError(err)


def move(src: str, dest: str):
    '''
    ARGS:
        src: Source path
        dest: Destination path

    Rename/Move file from source to destination
    '''
    try:
        CLIENT.files_move_v2(src, dest)
    except Exception as err:
        exceptions.DropboxFileError(err)


def copy(src: str, dest: str):
    '''
    ARGS:
        src: Path to source file
        dest: Path to destination file

    Copy file from src to destination on dropbox
    '''
    try:
        CLIENT.files_copy_v2(src, dest)
    except Exception as err:
        exceptions.DropboxFileError(err)


def delete(path: str):
    '''
    ARGS:
        path: Path for the file to be deleted

    Delete file from dropbox, if the path is a folder contents of the folder would
    be deleted
    '''
    try:
        CLIENT.files_delete_v2(path)
    except Exception as err:
        exceptions.DropboxFileError(err)


def exists(path: str):
    '''
    ARGS:
        path: Path to be checked

    Path to be checked for existence on dropbox
    '''
    folder_path = posixpath.dirname(path)

    try:
        entries, _= list_folder(folder_path)
        return any(m.path_lower == path.lower() for m in entries)
    except Exception as err:
        raise exceptions.DropboxFileError(err)


def list_folder(path: str) -> Tuple[List, str]:
    '''
    ARGS:
        path: Path to folder
    RETURNS:
       a pair of list of folder contents and a cursor representing  the current state
    '''
    try:
        result = CLIENT.files_list_folder(path)
        cursor = result.cursor
        flist = result.entries
        return flist, cursor
    except Exception as err:
        raise exceptions.DropboxFileError(err)


def list_folder_changes(cursor: str) -> Tuple[List, str]:
    '''
    ARGS:
        cursor: The cursor to the folder who's state is to be calculated
    RETURNS:
        a pair of list of folder changes and a new cursor
    '''
    try:
        result = CLIENT.files_list_folder_continue(cursor)
        cursor = result.cursor
        flist = result.entries
        return flist, cursor
    except Exception as err:
        raise exceptions.DropboxFileError(err)
