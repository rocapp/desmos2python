"""desmos2python pandoc wrapper methods"""
import os
import pypandoc as pdoc
import copy
import re
from desmos2python.utils import D2P_Resources
import importlib


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
    out = re.subn(string=plain, pattern=r'([\)\.0-9])([\(A-Za-z])', repl=r'\1*\2')
    if len(out) > 0:
        return out[0]
    return plain


def convert2plain(estr, clean_ws=True):
    """Convert generic input (e.g., latex) to pandoc plain format.

    Examples:
    ---------
    > convert2plain('T_{z}\\left(S,M,Y,X,B,x\\right)=S\\cdot\\left(\\pi\\cdot\\left(E\\left(\\left(M+0.7\\cdot E\\left(100\\cdot\\left(Y\\cdot\\left(\\tau_{y}-1.5\\right)\\right)\\right)-0.7E\\left(0.7\\left(X-Y\\right)\\right)\\right)\\right)-\\frac{0.5E\\left(0.3X\\right)}{1+M+0.23E\\left(Y\\right)}\\right)E\\left(M-1\\right)-Z_{tail}\\left(t_{z}\\left(x+1\\right),X,Y,B\\right)\\right)')
    'T_z(S,M,Y,X,B,x)=S*(π*(E((M+0.7*E(100*(Y*(τ_y-1.5)))-0.7*E(0.7*(X-Y))))-((0.5*E(0.3*X))/(1+M+0.23*E(Y))))*E(M-1)-Z_tail(t_z(x+1),X,Y,B))'
    """
    estr = copy.copy(estr)
    #: replace greek characters with unicode equivalents
    greek = importlib.import_module('resources.greek_chars', 'desmos2python') \
                     .GreekAlphabet()
    syms = {'\\cdot': '*', }
    syms.update({'\\'+k: v['uni'] for k, v in greek.df.to_dict().items()})
    repls = {}  # store complete map of replacements
    for k, v in syms.items():
        # handle fullname present in string
        if k in estr and k != '\\cdot':
            repls[v] = k
        # handle symbol found in string
        if v in estr:
            repls[k] = v
        estr = estr.replace(k, v)
    #: replace latex fractions with ( () / () )
    estr = replace_latex_fracs(estr)
    #: perform pandoc conversion step
    plain = pdoc.convert_text(source=estr, to='plain', format='latex')
    #: fix greek characters (back to full name)...
    for symbol, fullname in repls.items():
        estr = estr.replace(symbol, fullname).replace('\\', '')
    #: clean whitespace...
    if clean_ws is True:
        plain = plain.strip().replace('\n', '').replace('\r', '')
    #: fix any missing multiplication operators...
    plain = fix_missing_multop(plain)
    return plain
