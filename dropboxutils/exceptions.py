'''
Exception classes for dropbox utilities
'''


class DropboxUtilsException(Exception):
    '''
    Base exception for dropboxutils package
    '''


class ReaderException(DropboxUtilsException):
    '''
    Exception that occurs when reading
    files from dropbox
    '''


class WriterException(DropboxUtilsException):
    '''
    Exception that occurs when writing file
    to dropbox
    '''


class FileDownloadException(DropboxUtilsException):
    '''
    Exception raised when file download from dropbox
    fails
    '''


class FileUploadException(DropboxUtilsException):
    '''
    Exception raised when file upload to dropbox fails
    '''


class DropboxException(DropboxUtilsException):
    '''
    Exception that occurs during interataction with the
    dropbox API
    '''
