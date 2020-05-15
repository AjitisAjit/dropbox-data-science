'''
monitor
---------
'''

import time
import logging
from typing import Callable, Optional, List

from . import exceptions, folder


LOGGER = logging.getLogger('dropboxutils')


class DropboxMonitor():
    '''
    Attributes:
        folder: Folder to listen to
        emitter: Function to call when an event occurrs
        logger: Logs activity

    Monitors dropbox activity for changes
    '''

    def __init__(self, path: str, emit_function: Callable, logger: Optional[logging.Logger] = None):
        self._logger = logging.getLogger(
            'dropboxutils') if logger is None else logger
        self._folder = folder.DropboxFolder(path)
        self._emitter = emit_function

    def watch(self):
        while True:
            try:
                self._folder.update()
                flist = self._folder.flist()
                cursor = self._folder.cursor()
                self._publish(flist, cursor)
            except exceptions.DropboxFolder as err:
                self._logger.warning(err)
            finally:
                time.sleep(1)

    def emit(self, flist: List, cursor: str):
        try:
            self._emitter(cursor, flist)
        except Exception as err:
            raise exceptions.DropboxMonitorError(err)
