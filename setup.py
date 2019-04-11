#!/usr/bin/env python
"""File and Array resources for LF View API Python client"""

import setuptools

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.6',
    'License :: OSI Approved :: MIT License',
    'Topic :: Scientific/Engineering',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Operating System :: Unix',
    'Operating System :: MacOS',
    'Natural Language :: English',
]

with open('README.rst') as f:
    LONG_DESCRIPTION = ''.join(f.readlines())

setuptools.setup(
    name='lfview-resources-files',
    version='0.0.2',
    packages=setuptools.find_packages(exclude=('tests',)),
    install_requires=[
        'properties[full]>=0.5.6',
    ],
    author='Seequent',
    author_email='franklin.koch@seequent.com',
    description='Definitions and documentation for LF View file resources',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/x-rst',
    license='MIT',
    url='https://lfview.com',
    download_url='https://github.com/seequent/lfview-resources-files',
    classifiers=CLASSIFIERS,
    platforms=['Windows', 'Linux', 'Solaris', 'Mac OS-X', 'Unix'],
    use_2to3=False,
)
