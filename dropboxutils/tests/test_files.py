'''
test_files
--------------
'''

import posixpath
from .. import files


def test_list_folder(test_directory):
    folder_contents = files.list_folder(test_directory)
    flist, cursor = folder_contents
    assert not flist

    # Uploads an empty file
    arbitrary_filename = 'some_file_path'
    arbitrary_path = posixpath.join(test_directory, arbitrary_filename)
    files.upload(b'', arbitrary_path)

    new_contents = files.list_folder_changes(cursor)
    changes, new_cursor = new_contents
    assert changes
    assert new_cursor != cursor

    files.delete(arbitrary_path)
