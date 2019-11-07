'''Setup script'''

import setuptools


with open('README.md', 'r') as f:
    long_description = f.read()


setuptools.setup(
    name='dropbox-ds-AJIT-NATH',
    version='0.5.1',
    author='Ajit Nath',
    description='Provides data science utilities for dropbox',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    tests='tests',
    python_requires='>=3.7'
)
