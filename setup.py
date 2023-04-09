#!/usr/bin/env python

# stdlib
from pathlib import Path
import sys
import importlib
import logging

# 3rd party
from setuptools import setup

rootdir = str(Path('.').resolve())
if rootdir not in sys.path:
    sys.path.insert(0, rootdir)

setup(
    name = "desmos2python",
    setup_requires = ['numpy', 'docutils',],
)
