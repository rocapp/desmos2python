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

logger = logging.getLogger()
orig_lvl = logger.getEffectiveLevel()
logger.setLevel(logging.ERROR)
init_resources_d2p = \
    importlib \
    .import_module('._setuptools_ext', package='desmos2python') \
    .init_resources_d2p
logger.setLevel(orig_lvl)

setup(
    name = "desmos2python",
    setup_requires = ['numpy', 'docutils'],
    cmdclass = {"init_resources_d2p": init_resources_d2p},
)
