#!/usr/bin/env python

# stdlib
from pathlib import Path
import sys

# 3rd party
from setuptools import setup

setup(
    name="desmos2python",
    use_scm_version={"local_scheme": "node-and-timestamp"},
    setup_requires=['setuptools_scm'],
)
