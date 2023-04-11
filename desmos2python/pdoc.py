"""desmos2python pandoc wrapper methods"""
import os
import pypandoc as pdoc
import copy
import re
import sys
from pathlib import Path
module_root = Path(__file__).parents[1].__str__()
if module_root not in sys.path:
    sys.path.insert(0, module_root)
from desmos2python.utils import D2P_Resources
from desmos2python import greek
import importlib
import logging
import unicodedata
from typing import Tuple, Literal

logger = logging.getLogger(__name__)


def convert2html(s, opts=''):
    """Convert generic input (e.g., latex) to pandoc HTML format.

    Wraps around the pandoc CLI.
    """
    return os.popen(f"echo '{s}' | pandoc {opts}").read()


def replace_latex_fracs(estr):
    subs = re.subn(
        string=estr,
        pattern=r'\\frac{([a-zA-Z0-9\.\-\+\\\(\)]*)}{([a-zA-Z0-9\.\-\+\\\(\)]*)}',
        repl=r'\\left(\\left(\1\\right)/\\left(\2\\right)\\right)'
    )
    if len(subs) > 0:
        return subs[0]
    return estr


def fix_missing_multop(plain):
    """fix missing multiplication operators in post-conversion (latex->plain pandoc)"""
    out = re.subn(string=plain, pattern=r'((?!math\.|np\.)([\)0-9]))((?!^math\.|^np\.)([\(A-Za-z]))', repl=r'\1*\3')
    if len(out) > 0:
        return out[0]
    return plain


def fix_unicode(estr: str) -> str:
    """ref: https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize"""
    return unicodedata.normalize('NFKC', estr)


def convert2plain(estr: str, clean_ws = True, src_format='latex') -> str:
    """Convert generic input (e.g., latex) to pandoc plain format.

    Examples:
    ---------
    >>> print(convert2plain(r'T_{z}\\left(S,M,Y,X,B,x\\right)=S\\cdot\\left(\\pi\\cdot\\left(E\\left(\\left(M+0.7\\cdot E\\left(100\\cdot\\left(Y\\cdot\\left(\\tau_{y}-1.5\\right)\\right)\\right)-0.7E\\left(0.7\\left(X-Y\\right)\\right)\\right)\\right)-\\frac{0.5E\\left(0.3X\\right)}{1+M+0.23E\\left(Y\\right)}\\right)E\\left(M-1\\right)-Z_{tail}\\left(t_{z}\\left(x+1\\right),X,Y,B\\right)\\right)'))
    T_(z)*(S,M,Y,X,B,x)=S⋅(pi⋅(E((M+0.7⋅E(100⋅(Y⋅(tau_(y)−1.5)))−0.7*E(0.7*(X−Y))))−((0.5*E(0.3*X))/(1+M+0.23*E(Y))))*E(M−1)−Z_(tail)*(t_(z)*(x+1),X,Y,B))
    """
    estr = copy.copy(estr)
    
    if src_format == 'latex':
        #: replace latex fractions with ( () / () ) ! needed ahead of pandoc
        estr = replace_latex_fracs(estr)
        #: perform pandoc conversion step
        estr = pdoc.convert_text(source=f"${estr}$", to='plain', format='latex')
    #: fix unicode
    estr = fix_unicode(estr)
    #: replace greek chars
    estr, repls = greek.convert(estr, infmt='unicode', outfmt='plain')
    #: clean whitespace...
    if clean_ws is True:
        estr = estr.strip().replace('\n', '').replace('\r', '').replace(' ', '')
    #: fix any missing multiplication operators...
    estr = fix_missing_multop(estr)
    return str(estr)


if __name__ == '__main__':
    import doctest
    doctest.testmod()