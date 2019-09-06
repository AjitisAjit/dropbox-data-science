'''
Exception classes for dropbox utilities
'''


class DropboxException(Exception):
    '''
    Base exception for dropboxutils package
    '''


class DropboxFileError(DropboxException):
    '''
    Error occured when reading writing and listing
    files / directories on dropbox
    '''


class DropboxMonitorError(DropboxException):
    '''
    Error occured when monitoring a dropbox directory
    for changes
    '''


class DropboxLoggerError(DropboxException):
    '''
    Error logging to dropbox
    '''
