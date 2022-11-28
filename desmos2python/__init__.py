from setuptools_scm import get_version
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

#: other imports
import desmos2python.utils as utils
import desmos2python.latex as latex
from desmos2python.latex import DesmosLatexParser
import desmos2python.browser as browser
from desmos2python.browser import DesmosWebSession


__all__ = [
    'rootpath',
    'get_rootpath',
    'DesmosLatexParser',
    'DesmosWebSession',
]
