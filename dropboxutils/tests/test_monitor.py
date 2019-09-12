'''
Test monitor a folder on dropbox for changes
'''

import time
import posixpath
from queue import Queue
from threading import Thread

import pytest
from .. import monitor as mtr
from .. import files


@pytest.fixture(scope='module')
def monitor(test_directory):
    q = Queue()
    listener = mtr.Listener(test_directory, q)
    return listener, q


def test_monitor(test_directory, client, monitor):
    listener, q = monitor
    arr = list()
    handler = mtr.Handler(lambda x: arr.append(x), q)

    l_thread = Thread(target=listener.watch, daemon=True)
    h_thread = Thread(target=handler.watch, daemon=True)
    h_thread.start()
    l_thread.start()

    arbitrary_filename = 'some_file_path'
    arbitrary_path = posixpath.join(test_directory, arbitrary_filename)
    files.upload(b'', arbitrary_path)

    time.sleep(5)  # Waits for listener and handler to interact
    assert arr[0] == arbitrary_path
