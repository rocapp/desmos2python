#!/usr/bin/env python

"""The setup script."""

from setuptools import setup

setup(
    use_scm_version={
        'write_to': '_version.py',
        'write_to_template': '__version__ = "{version}"',
    },
    setup_requires=['setuptools_scm'],
)
