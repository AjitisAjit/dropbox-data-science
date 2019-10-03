'''
monitor
---------

Monitors a folder for addition of new files. The full paths to these new files
are published to a queue
'''

import os
import time
import queue
import logging
from typing import List, Callable

import dropbox

from . import exceptions, files


LOGGER = logging.getLogger('dropboxutils')


class Listener():
    '''
    Attributes:
        q: A shared queue, that the handler also listens to
        path: Folder to listen to for changes

    Listens to changes in the folder, if the folder is modified
    enques the path to the file onto a shared queue
    '''

    def __init__(self, path: str, q: queue.Queue):
        try:
            entries, cursor = files.list_folder(path)
        except Exception as err:
            raise exceptions.DropboxMonitorError(err)

        self._flist = entries
        self._cursor = cursor
        self._q = q

    def watch(self):
        while True:
            try:
                changes, new_cursor = files.list_folder_changes(self._cursor)
            except exceptions.DropboxFileError as err:
                LOGGER.warning(err)

            self._cursor = new_cursor
            flist = [f for f in changes if isinstance(f, dropbox.files.FileMetadata)]
            new_files = [f for f in flist if not any(o.name == f.name for o in self._flist)]

            if new_files:
                self.publish(new_files)

            self._flist = flist
            time.sleep(1)

    def publish(self, new_files: List):
        for m in new_files:
            try:
                self._q.put_nowait(m.path_lower)
            except Exception as err:
                raise exceptions.DropboxMonitorError(err)


class Handler:
    '''
    Attributes:
        q: Shared queue to that listeners puts filepaths on
        handler: Function that processes the data from the queue

    Handles paths obtained from a queue in a threadsafe manner
    '''

    def __init__(self, handler: Callable, q: queue.Queue):
        self._handler = handler
        self._q = q

    def watch(self):
        '''
        Monitors file queue for changes and calls handler function when a path is
        enqued
        '''
        while True:
            path = self._q.get()
            self._handler(path)
            time.sleep(1)
