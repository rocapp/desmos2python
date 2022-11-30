#!/usr/bin/env python

# stdlib
import pathlib
import sys

# 3rd party
from setuptools import setup

sys.path.append('.')

repo_root = pathlib.Path(__file__).parent

setup(
    name="desmos2python",
    use_scm_version={"local_scheme": "node-and-timestamp"},
    setup_requires=['setuptools_scm'],
    )
