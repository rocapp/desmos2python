#!/bin/bash
python3 -m pip install -r build-requirements.txt --upgrade
python3 -m build
python3 -m twine upload --repository testpypi dist/*
