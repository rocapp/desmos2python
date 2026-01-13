import json
import pandas as pd
from desmos2python.utils import D2P_Resources
from typing import (
    Union,
    Container,
    Literal,
    Tuple,
)
import numpy as np
from functools import cached_property

__all__ = [
    'GreekAlphabet',
    'greek',
    'convert_greek_chars',
]


#: choices for convert_greek_chars
FormatLiteral = Literal['latex', 'unicode', 'plain']


class GreekAlphabet:

    """Namespace for accessing the greek alphabet as (name, unicode symbol).

    ref: https://gist.githubusercontent.com/beniwohli/765262/raw/68980c0e2135777db9bd7cfdf1eea365dc8c68f9/greek_alphabet.py
    """

    def __init__(self):
        self.rpath = D2P_Resources.get_package_resources_path()
        self.d = json.loads(self.rpath.joinpath('greek_alphabet.json').read_text())
        #: access like: GreekAlphabet().df['Alpha'], output: 'A'
        self.df = pd.Series(self.d) \
                    .to_frame() \
                    .reset_index(names=['uni']) \
                    .set_index(0).T

    @cached_property
    def latex_names(self):
        return "\\" + self.names

    @cached_property
    def chars(self) -> np.ndarray:
        return self.df.values[0]

    @cached_property
    def names(self) -> np.ndarray:
        return self.df.columns.values

    def match_names(self, names: Container) -> Container:
        """return a vector of names found in the input vector"""
        return np.intersect1d(names, self.names)

    def match_chars(self, chars: Container) -> Container:
        """return a vector of characters found in the input vector"""
        return np.intersect1d(chars, self.chars)

    def extract_names(self, instr: str) -> list:
        """return a list of names found in the input string"""
        return [n for n in self.names if n in instr]

    def extract_latex_names(self, instr: str) -> list:
        """return a list of latex names found in input string"""
        return [n for n in self.latex_names if n in instr]

    def extract_chars(self, instr: str) -> list:
        """return a list of unicode characters found in the input string"""
        return [c for c in self.chars if c in instr]

    def _get(self, name: str, as_item = True) -> str:
        """given a name (e.g. 'alpha'), return the unicode character (e.g., 'α').
        """
        if name in self.df.columns:
            if as_item is True:
                return self.df[name].item()
            return self.df[name]
        else:
            return self.get_from_unicode(name)

    @property
    def _get_vectorized(self):
        return np.vectorize(self._get)

    def get(self, name: Union[str, Container], as_item=True) -> Union[str, Container]:
        return self._get_vectorized(name, as_item=as_item)

    def get_from_unicode(self, uni: str) -> str:
        """given a unicode character (e.g. α), return the name (e.g., 'alpha').
        """
        cols = [c for c in self.df.columns if self.df[c].item() == uni]
        if len(cols) == 0:
            raise RuntimeError(f"no greek character matching given name: '{uni}'")
        return cols[0]

    def convert(self, estr: str,
                infmt: FormatLiteral = 'latex',
                outfmt: FormatLiteral = 'unicode',
                ignore_operators=True, ignore=[]) -> Tuple:
        """convert between latex <-> unicode representations of greek characters.

        Arguments:
        ----------
        - estr: input string to be converted
        - infmt: input format
        - outfmt: output format
        - ignore_operators: if true, ignore builtin operators (for now just \\cdot or * for multiplication)
        - ignore: list of  any extra symbols to ignore.

        returns: (new string, replacement dict)
        """
        if ignore_operators is True:
            plainops = ['*']
            latexops = []
            operators = plainops + latexops  # operators to ignore
            ignore.extend(operators)
            #: init syms map of { input_syms -> output_syms }
        match (infmt, outfmt):
            case ('latex', 'unicode'):
                syms = dict(zip(latexops, plainops))
                syms.update(zip(self.latex_names, self.chars))
                extract = self.extract_latex_names
            case ('latex', 'plain'):
                syms = dict(zip(latexops, plainops))
                syms.update(zip(self.latex_names, self.names))
                extract = self.extract_latex_names
            case ('unicode', 'latex'):
                syms = dict(zip(plainops, latexops))
                syms.update(zip(self.chars, self.latex_names))
                extract = self.extract_chars
            case ('unicode', 'plain'):
                syms = dict(zip(self.chars, self.names))
                extract = self.extract_chars
                repls = {}  # store complete map of { found_symbols -> corresponding_replacements }
                #: get replacements (without those to be ignored)
        repls = {extracted: syms[extracted] for extracted in extract(estr) if extracted not in ignore}
        #: apply replacements
        for symbol, replacement in repls.items():
            estr = estr.replace(symbol, replacement)
        return (estr, repls)


#: instantiate for global access
greek = GreekAlphabet()


def convert_greek_chars(estr: str, infmt : FormatLiteral = 'latex', ignore_operators=True, ignore=[]) -> Tuple:
    """go between latex <-> unicode representations of greek characters.

    Arguments:
    ----------
    - infmt: input format (output will be the other)

    return: new string, replacement dict
    """
    return greek.convert(estr, infmt=infmt, outfmt=outfmt, ignore_operators=ignore_operators, ignore=ignore)
