'''Setup script'''

import setuptools


with open('README.md', 'r') as f:
    long_description = f.read()


setuptools.setup(
    name='dropbox-ds',
    version='0.5.7',
    author='Ajit Nath',
    description='Provides data science utilities for dropbox',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['dropbox_ds'],
    tests='dropbox_ds/tests',
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'dropbox>=9.4.0',
        'pandas>=0.25.3',
        'xlrd>=1.2.0'
    ],
    python_requires='>=3.7'
)
