'''
Test dropbox folder operations
'''

from .. import folder, file


def test_update(folder_instance, dropbox_file):

    folder_instance.update()
    assert isinstance(folder_instance.cursor, str)
    assert isinstance(folder_instance.flist, list)
    assert not folder_instance.flist
    c1 = folder_instance.cursor

    upload_files(dropbox_file)
    folder_instance.update()
    assert isinstance(folder_instance.cursor, str)
    assert folder_instance.cursor != c1

    assert isinstance(folder_instance.flist, list)
    class_list = [f.__class__.__name__ for f in folder_instance.flist]
    assert sorted(class_list) == sorted([
        file.DropboxTextFile.__name__,
        file.DropboxCsvFile.__name__,
        file.DropboxExcelFile.__name__
    ])


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
