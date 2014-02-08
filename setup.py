#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='robobrowser',
    version='0.1.0',
    description='Your friendly neighborhood web scraper',
    author='Joshua Carp',
    author_email='jm.carp@gmail.com',
    url='https://github.com/jmcarp/robobrowser',
    packages=[
        'robobrowser',
    ],
    package_dir={'robobrowser': 'robobrowser'},
    include_package_data=True,
    install_requires=[
        'nose',
        'responses',
    ],
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
    ],
    test_suite='tests',
)
