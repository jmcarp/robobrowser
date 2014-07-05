#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


from setuptools import setup, find_packages
from pip.req import parse_requirements

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')
requirements = [
    str(requirement.req)
    for requirement in parse_requirements('requirements.txt')
]

setup(
    name='robobrowser',
    version='0.3.1',
    description='Your friendly neighborhood web scraper',
    author='Joshua Carp',
    author_email='jm.carp@gmail.com',
    url='https://github.com/jmcarp/robobrowser',
    packages=find_packages(),
    package_dir={'robobrowser': 'robobrowser'},
    include_package_data=True,
    install_requires=requirements,
    tests_require=[
        'nose',
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
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
)
