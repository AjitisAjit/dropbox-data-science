'''Setup script'''

from setuptools import setup, find_packages

setup(
    name='dropboxutils',
    version='0.21',
    description='dropbox utitities for reading, writing and monitoring files on dropbox',
    packages=find_packages(),
    tests='tests',
    install_requires=['requests', 'dropbox']
)
