#!/bin/bash
rm dist/desmos2python-*{.tar.gz,.whl}
python3 -m pip install -r build-requirements.txt --upgrade
python3 -m build
