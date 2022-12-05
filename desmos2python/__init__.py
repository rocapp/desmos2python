from pathlib import Path
import sys


def get_rootpath(startpath=__file__):
    #: package root path
    rootpath = Path(startpath).parent
    return rootpath


#: top-level root path
rootpath = get_rootpath()

#: insert to sys.path if needed.
if rootpath not in sys.path:
    sys.path.insert(0, rootpath)

#: d2p api-level imports
import desmos2python.utils as utils

import desmos2python.latex as latex
from desmos2python.latex import DesmosLatexParser

import desmos2python.browser as browser
from desmos2python.browser import DesmosWebSession

import desmos2python.api as api
from desmos2python.api import (
    make_latex_parser, make_web_session,
    export_graph_and_parse,
)


__all__ = [
    'rootpath',
    'get_rootpath',
    'DesmosLatexParser',
    'DesmosWebSession',
    'make_latex_parser',
    'make_web_session',
    'export_graph_and_parse',
]
