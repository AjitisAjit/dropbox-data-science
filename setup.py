'''Setup script'''

import setuptools


with open('README.md', 'r') as f:
    long_description = f.read()


setuptools.setup(
    name='dropbox-ds-AJIT-NATH',
    version='0.5.2',
    author='Ajit Nath',
    description='Provides data science utilities for dropbox',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    tests='dropbox_ds/tests',
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7'
)
