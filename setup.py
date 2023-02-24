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


def get_version():
    from setuptools_scm.version import guess_next_simple_semver
    def clean_scheme(version):
        return guess_next_simple_semver(version, retain=3, increment=True)
    return {'local_scheme': clean_scheme}

setup(
    name = "desmos2python",
    cmdclass = {"init_resources_d2p": init_resources_d2p},
    use_scm_version={
        'tag_regex': r'^(?P<prefix>v)?(?P<version>[^\+]+)(?P<suffix>.*)?$',
        'write_to_template': '__version__ = "{version}"',
        'write_to': 'desmos2python/_version.py',
    },
    setup_requires = ['numpy', 'docutils', 'setuptools_scm'],
)
