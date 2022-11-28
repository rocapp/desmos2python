#!/bin/bash
tag=$(python3 -c $'import setuptools_scm as scm; print("{}".format(scm.version_from_scm(".").tag.base_version))')
git tag "v$tag"
twine upload dist/*$tag*
