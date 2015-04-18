# -*- coding: utf-8 -*-

import os
import re
import sys

from setuptools import setup
from setuptools import find_packages


REQUIREMENTS = [
    'beautifulsoup4>=4.3.2',
    'requests>=2.6.0',
    'six>=1.9.0',
    'Werkzeug>=0.10.4',
]
TEST_REQUIREMENTS = [
    'coverage',
    'coveralls',
    'docutils',
    'mock',
    'nose',
    'sphinx',
    'tox',
]


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


def find_version(fname):
    """Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    """
    version = ''
    with open(fname, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version


setup(
    name='robobrowser',
    version=find_version('robobrowser/__init__.py'),
    description='Your friendly neighborhood web scraper',
    author='Joshua Carp',
    author_email='jm.carp@gmail.com',
    url='https://github.com/jmcarp/robobrowser',
    packages=find_packages(exclude=('tests',)),
    package_dir={'robobrowser': 'robobrowser'},
    include_package_data=True,
    install_requires=REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS,
    license='MIT',
    zip_safe=False,
    keywords='robobrowser',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
)
