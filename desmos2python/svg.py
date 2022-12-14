"""Parse Desmos SVG screenshots -> plottable"""
from functools import cached_property
from svg.path import parse_path
from svg.path.path import Line
from xml.dom import minidom
from desmos2python.utils import D2P_Resources
from typing import NamedTuple, Sequence
import numpy as np
import pandas as pd


class PyPoint(NamedTuple):
    x0: float
    x1: float
    y0: float
    y1: float


class PyPath(NamedTuple):
    
    points: Sequence[PyPoint] = []

    @property
    def x0(self):
        return [pt.x0 for pt in self.points]

    @property
    def x1(self):
        return [pt.x1 for pt in self.points]

    @property
    def y0(self):
        return [pt.y0 for pt in self.points]

    @property
    def y1(self):
        return [pt.y1 for pt in self.points]


class DesmosSVGParser:
    """Parse Desmos SVG screenshots -> xmltree, plottable data"""
    
    @cached_property
    def resources_path(self):
        return D2P_Resources.get_package_resources_path()

    @cached_property
    def user_path(self):
        return D2P_Resources.get_user_resources_path()
    
    def __init__(self, filename='ex.svg', auto_init=True):
        self.fpath = self._setup_fpath(filename)
        self.doc = None
        if auto_init is True:
            self.init_doc()

    def _setup_fpath(self, filename):
        paths = [
            self.resources_path.joinpath("screenshots", filename),
            self.user_path.joinpath("screenshots", filename),
        ]
        for path in paths:
            if path.exists():
                return path
            matching = path.parent.rglob(f'*{filename}*' \
                                         .replace('**', '*'))
            for match in matching:
                return match
        raise RuntimeError('no matching filename found in ~/.desmos2python/screenshots.')

    def init_doc(self):
        self.doc = minidom.parse(self.fpath.__str__())

    def close_doc(self):
        self.doc.unlink()

    @cached_property
    def paths(self):
        paths = list(self.doc.getElementsByTagName('path'))
        return paths

    @cached_property
    def path_strings(self):
        path_strings = [path.getAttribute('d') for path in self.paths]
        return path_strings

    @cached_property
    def py_paths(self):
        py_paths = []
        for path_string in self.path_strings:
            try:
                path = parse_path(path_string)
            except TypeError:
                continue
            py_path = PyPath()
            for e in path:
                if isinstance(e, Line):
                    py_point = PyPoint(x0 = e.start.real,
                                       y0 = e.start.imag,
                                       x1 = e.end.real,
                                       y1 = e.end.imag)
                    py_path.points.append(py_point)
            y_pth = np.unique(py_path.y0).tolist() + \
                np.unique(py_path.y1).tolist()
            x_pth = np.unique(py_path.x0).tolist() + \
                np.unique(py_path.x1).tolist()
            if len(y_pth) > 1 and len(x_pth) > 1:
                py_paths.append(py_path)
        return py_paths

    def plot(self):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        for k, pth in enumerate(self.py_paths):
            x = pth.x0 + pth.x1
            ix = np.argsort(x)
            y = pth.y0 + pth.y1
            y = np.array(y)[ix]
            ax.plot(x, y, label=f'{k}')
        return fig, ax
