#!/usr/bin/env python
# This file is managed by 'repo_helper'. Don't edit it directly.

# stdlib
import pathlib
import shutil
import sys

# 3rd party
from setuptools import setup

sys.path.append('.')

repo_root = pathlib.Path(__file__).parent


def myversion():

    def clean_scheme(version):
        return '.'.join([str(v) for v in version.tag.public.split('.')[:1]])
    return {'local_scheme': clean_scheme}


setup(description="seamless conversion between Desmos LaTeX equations & " +
      "executable Python code.", name="desmos2python",
      use_scm_version=myversion, setup_requires=['setuptools_scm'])

shutil.rmtree("desmos2python.egg-info", ignore_errors=True)
