#!/bin/bash
rm dist/desmos2python-*{.tar.gz,.whl}
python3 -m pip install -r build-requirements.txt --upgrade
python3 -m build

# get tag
tag=$(python setup.py --version)

#: set appropriate git tag
git tag $tag
echo "to git: ${tag}"

tag=$(git describe --tags --abbrev=3)
echo "from git: ${tag}"

# build with Docker...
docker build . -t desmos2python:latest -t "desmos2python:${tag}" &&
    docker push desmos2python:latest "desmos2python:${tag}"

echo -e "...done with build step."