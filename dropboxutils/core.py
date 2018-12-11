'''
Core utilities used by dropbox. To create a dropbox client
define an environment variable `DROPBOX_API_TOKEN` with
dropbox api key
'''

import os
import dropbox


TOKEN = os.environ.get('DROPBOX_API_TOKEN')

CLIENT = dropbox.Dropbox(TOKEN)
