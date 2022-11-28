#!/bin/bash
old_tag=$(python3 -c $'import setuptools_scm as scm; print("{}".format(scm.version_from_scm(".").tag.base_version))')
tag=$(python3 -c $'import setuptools_scm as scm; print(".".join(scm.get_version().split(".")[:3]))')
git tag "v$tag"
git push --tags
twine upload dist/*$tag*
