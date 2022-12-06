import traceback
from pathlib import Path
import sys
import logging


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
import desmos2python.utils
import desmos2python.utils as utils
try:
    import desmos2python.latex as latex
    from desmos2python.latex import DesmosLatexParser
except ModuleNotFoundError:
    #: ! these try-except blocks are needed for custom setuptools command
    logging.warning(traceback.format_exc())

try:
    import desmos2python.browser as browser
    from desmos2python.browser import DesmosWebSession
except ModuleNotFoundError:
    logging.warning(traceback.format_exc())

try:
    import desmos2python.api as api
    from desmos2python.api import (
        make_latex_parser, make_web_session,
        export_graph_and_parse,
    )
except ModuleNotFoundError:
    logging.warning(traceback.format_exc())


__all__ = [
    'rootpath',
    'get_rootpath',
    'DesmosLatexParser',
    'DesmosWebSession',
    'make_latex_parser',
    'make_web_session',
    'export_graph_and_parse',
]
