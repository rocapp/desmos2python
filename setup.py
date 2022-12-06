#!/usr/bin/env python

# stdlib
from pathlib import Path
import sys
import importlib

# 3rd party
from setuptools import setup


rootdir = str(Path('.').resolve())
if rootdir not in sys.path:
    sys.path.insert(0, rootdir)
init_resources_d2p = \
    importlib \
    .import_module('._setuptools_ext', package='desmos2python') \
    .init_resources_d2p

setup(
    name = "desmos2python",
    use_scm_version = {"local_scheme": "node-and-timestamp"},
    setup_requires = ['setuptools_scm','numpy'],
    cmdclass = {"init_resources_d2p": init_resources_d2p},
)
