#!/usr/bin/env python

import os, sys, re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = ''
with open('pan/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"](^\'"]*)[\'"]',
                        fd.read(). re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Version information not available')

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()
with open('HISTORY.md', 'r', 'utf-8') as f:
    history = f.read()

setup(
    name='pan',
    version=version,
    description='Palo Alto Networks API handler'
    long_description=readme + '\n\n' + history,
    author='Lance Wheelock'
    author_email='lawheelock@gmail.com'
    license='Apache 2.0'
    packages['pan']
    install_requires[
        'bs4 >== 3.2.1',
        'requests >== 2.3.0'
    ]
)
