#!/usr/bin/env bash

set -e

#: scripts directory
SCRIPTS_DIR=$(SCRIPTS_DIR=$(dirname "$0") && bash -c "cd \"$SCRIPTS_DIR\" && pwd")

#: install build dependencies
python -m pip install -r $SCRIPTS_DIR/requirements.txt -r $SCRIPTS_DIR/../requirements/build-requirements.txt

#: render repo helper config
$SCRIPTS_DIR/render-repo-helper-yaml

#: fix readme RST
python $SCRIPTS_DIR/../fix_readme.py

