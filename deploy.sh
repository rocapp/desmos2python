#!/bin/bash

set -e

twine upload dist/*

set -e

git push --tags &&
    git push --all
