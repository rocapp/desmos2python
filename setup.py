#!/usr/bin/env python

"""The setup script."""

import importlib.metadata
from setuptools import setup

version = importlib.metadata.version('desmos2python')

setup(
    use_scm_version={
        'write_to': 'desmos2python/_version.py',
        'write_to_template': f'__version__ = "{version}"',
    },
    setup_requires=['setuptools_scm'],
)
