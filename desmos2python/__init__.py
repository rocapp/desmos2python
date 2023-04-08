import traceback
from pathlib import Path
import sys
import logging
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("desmos2python")
except PackageNotFoundError:
    # package is not installed
    pass


def get_rootpath(startpath=__file__):
    #: package root path
    rootpath = Path(startpath).parent
    return rootpath


#: top-level root path
rootpath = str(get_rootpath())

#: insert to sys.path if needed.
if rootpath not in sys.path:
    sys.path.append(rootpath)

# d2p api-level imports...

import desmos2python.utils
import desmos2python.utils as utils
from desmos2python.utils import D2P_Resources

greek = None
try:
    import desmos2python.resources as resources
except ModuleNotFoundError:
    logging.warn('failed to import d2p resources, greek alphabet might not be available.', exc_info=1)
else:
    from desmos2python.resources import greek
    from desmos2python.resources import convert_greek_chars

convert2plain = None
try:
    import desmos2python.pdoc as pdoc
except ModuleNotFoundError:
    logging.warning('failed to import pdoc utils.', exc_info=1)
else:
    from desmos2python.pdoc import convert2plain

try:
    import desmos2python.latex as latex
    from desmos2python.latex import DesmosLatexParser
except ModuleNotFoundError:
    #: ! these try-except blocks are needed for custom setuptools command
    logging.warning('failed to import latex utils.', exc_info=1)

try:
    import desmos2python.browser as browser
    from desmos2python.browser import DesmosWebSession
except ModuleNotFoundError:
    logging.warning('failed to import web utils.', exc_info=1)

try:
    import desmos2python.api as api
    from desmos2python.api import (
        make_latex_parser,
        make_web_session,
        make_svg_parser,
        export_graph_and_parse,
    )
except ModuleNotFoundError:
    logging.warning('failed to import high-level api.', exc_info=1)

make_web_session_with_state = None
try:
    import desmos2python.render as render
except ModuleNotFoundError:
    logging.warning('failed to import render api.', exc_info=1)
else:
    from desmos2python.render import make_web_session_with_state


__all__ = [
    'D2P_Resources',
    'rootpath',
    'get_rootpath',
    'DesmosLatexParser',
    'DesmosWebSession',
    'make_latex_parser',
    'make_web_session',
    'make_svg_parser',
    'export_graph_and_parse',
    'make_web_session_with_state',
    'convert2plain'
]
