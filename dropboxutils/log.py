'''
log.py
-------

Provides functionality for logging files to a dropbox folder
If the length of the log file exceeds limit, a new fille is written
similiar to rotatint file handler
'''

import io
import time
import logging

from . import files


class DropboxFileHandler(logging.FileHandler):
    '''
    Subclasses file handler and uploads records
    a file on dropbox. Open method creates a string buffer
    which is eventually  uploaded to a file on dropbox

    Attributes:
       path: Path to the file on dropbox
       encoding: File encoding, default: utf-8
    '''

    def __init__(self, path: str, encoding='utf-8'):
        self.encoding = encoding
        super().__init__(path, encoding=encoding)

    def _open(self):
        return io.StringIO()

    def emit(self, record):
        try:
            super().emit(record)
            self._upload()
        except Exception:
            self.handleError(record)

    def _upload(self):
        binary_data = self.stream.getvalue().encode(self.encoding)
        files.upload_data(binary_data, self.baseFilename)

    def close(self):
        '''
        Close StringIO instance and upload the
        data to dropbox
        '''
        if self.stream:
            try:
                # self._upload()
                self.flush()
            finally:
                stream = self.stream
                self.stream = None
                if hasattr(stream, "close"):
                    stream.close()


class DropboxRotatingFileHandler(DropboxFileHandler):
    '''
    An implementation of RotatingFileHandler as descriped here:
    http://github.com/python/cpython/Lib/logging/handlers.py.
    Adapted to be used with dropbox

    Attributes:
        path: Path to log file on dropbox
        max_bytes: Maximum number of bytes a file can hold before rotation
        backup_count: Number of log files to be rotated
    '''

    def __init__(self, path: str, max_bytes: int, backup_count: int):
        super().__init__(path)
        self.max_bytes = max_bytes
        self.backup_count = backup_count

    def do_rollover(self):
        '''
        Do a rollover, as described in __init__()
        '''
        if self.stream:
            self.stream.close()
            self.stream = None

        if self.backup_count > 0:
            for i in range(self.backup_count - 1, 0, -1):
                sfn = '{}.{}'.format(self.baseFilename, i)
                dfn = '{}.{}'.format(self.baseFilename, i + 1)

                if files.exists(sfn):
                    files.move(sfn, dfn)

            dfn = self.baseFilename + ".1"
            files.move(self.baseFilename, dfn)
            self.stream = self._open()

    def emit(self, record):
        '''
        Emit a record.
        Output the record to the file, catering for rollover as described
        in doRollover().
        '''

        if len(self.format(record)) > self.max_bytes:
            return  # Ignore messages larger than max size

        try:
            if self.should_rollover(record):
                self.do_rollover()
                time.sleep(1)

            super().emit(record)
        except Exception:
            self.handleError(record)

    def should_rollover(self, record: logging.LogRecord):
        '''
        Determine if rollover should occur.
        Basically, see if the supplied record would cause the file
        to rollover
        '''
        should_roll = False

        if self.stream is None:
            self.stream = self._open()

        if self.max_bytes > 0:
            msg = "%s\n" % self.format(record)

            if self.stream.tell() + len(msg) >= self.max_bytes:
                should_roll = True

        return should_roll
