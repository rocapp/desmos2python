#!/bin/bash
rm -r build/*
rm -r dist/*
rm -r desmos2python.egg-info/*

# stop on failure
set -e
set -o pipefail

tox -r -e build

# tags
old_tag=$(python3 -c $'import setuptools_scm as scm; print("{}".format(scm.version_from_scm(".").tag.base_version))') && \
        echo "old tag: ${old_tag}"

tag=$(python3 -c $'import setuptools_scm as scm; print(".".join(scm.get_version().split(".")[:3]))')
echo "proposed tag: ${tag}"

set -e

echo "Press any key to continue"
while [ true ] ; do
read -t 3 -n 1
if [ $? = 0 ] ; then
exit ;
else
echo "waiting for the keypress"
fi
done

echo "using proposed tag..."

git tag "v$tag"
echo "new tag: $(git describe --tags)"


# build with Docker...
docker build . -t desmos2python:latest -t "desmos2python:${tag}" && \
    docker push desmos2python:latest "desmos2python:${tag}"

echo -e "...done with build step."