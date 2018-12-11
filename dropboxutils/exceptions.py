'''
Exception classes for dropbox utilities
'''


class DropboxUtilsException(Exception):
    '''
    Base exception for dropboxutils package
    '''
    pass


class ReaderException(DropboxUtilsException):
    '''
    Exception that occurs when reading
    files from dropbox
    '''
    pass


class DropboxException(DropboxUtilsException):
    '''
    Exception that occurs during interataction with the
    dropbox API
    '''
    pass
