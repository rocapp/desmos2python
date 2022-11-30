#!/bin/bash
rm -r build/*
rm -r dist/*
rm -r desmos2python.egg-info/*

# stop on failure
set -e
set -o pipefail

tox -r -e prebuild -e build

# tags
python3.8 -m pip install setuptools-scm
old_tag=$(python3.8 -c $'import setuptools_scm as scm; print("{}".format(scm.version_from_scm(".").tag.base_version))') && \
        echo "old tag: ${old_tag}"

cmd='print("'$(python3.8 setup.py --version)'".split("+")[0])'
tag=$(python3.8 -c $cmd)
echo "proposed tag: ${tag}"

set -e

echo "using proposed tag..."

git tag "v$tag"
echo "new tag: $(git describe --tags)"

# build with Docker...
docker build . -t desmos2python:latest && \
    docker push desmos2python:latest

echo -e "...done with build step."