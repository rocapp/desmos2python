#!/usr/bin/env bash

# fail on error
set -e

python -m build

echo -e "...done with build step.\n"

ls ./dist/
