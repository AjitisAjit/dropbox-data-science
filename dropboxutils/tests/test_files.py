'''
test_files
--------------
'''

from .. import files


def test_list_folder(test_directory):
    folder_contents = files.list_folder(test_directory)
    assert not folder_contents
