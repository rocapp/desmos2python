#!/usr/bin/env python

"""The setup script."""

from setuptools import setup


def myversion():
    
    def clean_scheme(version):
        return '.'.join([str(v) for v in version.tag.public.split('.')[:1]])
    return {'local_scheme': clean_scheme}


setup(
    use_scm_version=myversion,
    setup_requires=['setuptools_scm'],
)
