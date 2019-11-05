'''
Exception classes for dropbox utilities
'''


class DropboxException(Exception):
    '''
    Base exception for dropboxutils package
    '''


class DropboxFileError(DropboxException):
    '''
    Error occured when reading writing or listing
    files
    '''


class DropboxFolderError(DropboxException):
    '''
    Errors when reading, writing or listing
    folder contents

    '''


class DropboxLoggerError(DropboxException):
    '''
    Error logging to dropbox
    '''
