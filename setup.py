#!/usr/bin/env python
# This file is managed by 'repo_helper'. Don't edit it directly.

# stdlib
import pathlib
import sys

# 3rd party
from setuptools import setup

sys.path.append('.')

repo_root = pathlib.Path(__file__).parent


def clean_scheme(version, **kwds):
    v = version.tag.public.split('+')[0]
    return v


setup(
    name="desmos2python",
    use_scm_version={'local_scheme': "no-local-version",
                     },
    setup_requires=['setuptools_scm'],
    )
