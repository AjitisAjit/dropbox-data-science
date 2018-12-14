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


class FileDownloadException(DropboxUtilsException):
    '''
    Exception raised when file download from dropbox
    fails
    '''
    pass


class FileUploadException(DropboxUtilsException):
    '''
    Exception raised when file upload to dropbox fails
    '''
    pass


class DropboxException(DropboxUtilsException):
    '''
    Exception that occurs during interataction with the
    dropbox API
    '''
    pass
