'''
Test dropbox folder operations
'''

import posixpath
from .. import dropboxfile, dropboxfolder


class TestUpdateFolder:

    def test_add_files(self, folder_instance, dropbox_file):
        folder_instance.update()
        assert isinstance(folder_instance.cursor, str)
        assert isinstance(folder_instance.flist, list)
        flist_1 = folder_instance.flist
        c1 = folder_instance.cursor

        upload_files(dropbox_file)
        folder_instance.update()
        flist_2 = folder_instance.flist
        c2 = folder_instance.cursor

        assert c1 != c2
        assert flist_1 == []
        assert sorted(list(map(lambda f: f.__class__.__name__, flist_2))) == sorted([
            dropboxfile.DropboxTextFile.__name__,
            dropboxfile.DropboxCsvFile.__name__,
            dropboxfile.DropboxExcelFile.__name__
        ])

    def test_move_files(self, folder_instance, dropbox_file):
        upload_files(dropbox_file)
        folder_instance.update()
        c1 = folder_instance.cursor
        flist_1 = folder_instance.flist

        # Move a file
        folder_path = folder_instance.path
        new_folder_path = posixpath.join(folder_path, 'old')
        new_folder = dropboxfolder.DropboxFolder(new_folder_path)
        new_folder.create()

        # Pick a random file and move it there
        first, *rest = flist_1
        first_path = first.path
        new_path = posixpath.join(new_folder_path, posixpath.basename(first_path))
        first.move(new_path)

        folder_instance.update()
        c2 = folder_instance.cursor
        flist_2 = folder_instance.flist

        assert set(flist_1) - set(flist_2) == set([first])
        assert c1 != c2

    def test_delete_file(self, folder_instance, dropbox_file):
        upload_files(dropbox_file)
        folder_instance.update()
        c1 = folder_instance.cursor
        flist_1 = folder_instance.flist

        first, *rest = flist_1
        first.delete()

        folder_instance.update()
        c2 = folder_instance.cursor
        flist_2 = folder_instance.flist

        assert set(flist_1) - set(flist_2) == set([first])
        assert c1 != c2

    def test_update_file(self, folder_instance, dropbox_file):
        upload_files(dropbox_file)
        folder_instance.update()
        c1 = folder_instance.cursor
        flist_1 = folder_instance.flist

        first, *rest = flist_1
        first.upload(b'modified content')

        folder_instance.update()
        c2 = folder_instance.cursor
        flist_2 = folder_instance.flist

        assert set(flist_1) - set(flist_2) == set()
        assert c1 != c2


def upload_files(dropbox_file):
    text_data = dropbox_file('test.txt')
    excel_data = dropbox_file('test.xlsx')
    csv_data = dropbox_file('test.csv')

    text_data = dropbox_file('test.txt')
    text_file = text_data['file']
    text_payload = text_data['payload']

    csv_data = dropbox_file('test.csv')
    csv_file = csv_data['file']
    csv_payload = csv_data['payload']

    excel_data = dropbox_file('test.xlsx')
    excel_file = excel_data['file']
    excel_payload = excel_data['payload']

    text_file.upload(text_payload)
    csv_file.upload(csv_payload)
    excel_file.upload(excel_payload)
