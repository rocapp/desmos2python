#!/bin/bash
python3 -m twine upload dist/*$(git tag | tail -1)*
