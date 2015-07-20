#!/usr/bin/env python

import os, sys, re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='pan',
    version='0.0.1',
    description='Palo Alto Networks API handler',
    author='Lance Wheelock',
    author_email='lawheelock@gmail.com',
    license='Apache 2.0',
    packages=['pan'],
    install_requires=[
        'beautifulsoup4',
        'requests',
    ],
)
