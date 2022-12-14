"""desmos2python.api: high-level API access, helper methods."""
from desmos2python.latex import DesmosLatexParser
from desmos2python.browser import DesmosWebSession
from desmos2python.svg import DesmosSVGParser

__all__ = [
    'make_latex_parser',
    'make_web_session',
    'make_svg_parser',
    'export_graph_and_parse',
]


def make_svg_parser(filename, auto_init=True):
    return DesmosSVGParser(filename=filename, auto_init=auto_init)


def make_latex_parser(fpath, **kwds):
    return DesmosLatexParser(fpath=fpath, **kwds)


def make_web_session(url, **kwds):
    return DesmosWebSession(url=url, **kwds)


def export_graph_and_parse(url, kwds_dws={}, kwds_dlp={}, retall=True):
    """High-level method to quickly export/download from a Desmos graph, automatically parse to executable python code."""
    dws = make_web_session(url, **kwds_dws)
    fpath_json = dws.export_latex2json()
    dlp = make_latex_parser(fpath=fpath_json, **kwds_dlp)
    if retall is False:
        return dlp
    elif retall is True:
        return (dws, dlp)
