from queue import Queue
from os import PathLike
import inspect
import logging
import json
import re
import traceback
from pathlib import Path
from functools import cached_property
import sympy as sp
from sympy.parsing.latex import parse_latex
from sympy import pycode
from jinja2 import Environment, FileSystemLoader
from typing import AnyStr, List, Dict, Union, Container
from desmos2python._logger import LoggingContext
from desmos2python.consts import GlobalConsts
from desmos2python.utils import flatten, D2P_Resources
import builtins

__all__ = [
    'DesmosLinesContainer',
    'DesmosLatexParser',
]    

#: update builtin globals with numerical constants
builtins.__dict__.update(vars(GlobalConsts))

#: instantiate namespace-specific logger
logger = logging.getLogger(__name__)


class DesmosLinesContainer:

    """wrapper to avoid warnings/errors for ipython tab-completion.

    ref: https://ipython.readthedocs.io/en/stable/config/integrating.html#tab-completion
    """
    
    def __init__(self, lines=[]):
        self._lines = []
        self.lines = lines

    @property
    def lines(self):
        if self._lines is None:
            self._lines = []
        return self._lines
    @lines.setter
    def lines(self, new):
        if new is None:
            self._lines = []
            return
        if isinstance(new, DesmosLinesContainer):
            new = new.lines
        self._lines = new

    def __len__(self):
        return len(self.lines)

    def _ipython_key_completions_(self):
        return ['lines', ]

    def __str__(self):
        head = f'{self.__class__.__name__}(length={len(self.lines):03d})'
        tail = str(self.lines)
        if len(tail) > 100:
            tail = tail[:100] + '\n...' + tail[-100:].rstrip(']') + '\n...]'
        return f'{head}\n{tail}'

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, item):
        return self.lines[item]

    def __setitem__(self, item, value):
        self.lines[item] = value

    def __iter__(self):
        return iter(self.lines)

    def __getattribute__(self, name):
        return object.__getattribute__(self, name)

    def __getattr__(self, name):
        """use the corresponding attribute in `self.lines` if not otherwise defined"""
        return object.__getattribute__(self.lines, name)

    @property
    def empty(self):
        """flag indicates whether wrapped list is empty or not"""
        return len(self.lines) == 0


class DesmosLatexParser:

    """Helper class for parsing Desmos LaTeX equations.
    """

    def _ipython_key_completions_(self):
        return []

    def __init__(self, expr_str: AnyStr = None, lines: List[AnyStr] = None,
                 fpath: AnyStr = None, auto_init: bool = True, auto_exec: bool = True,
                 ns_prefix: AnyStr = '', ns_name: AnyStr = 'DesmosModelNS', **kwds):
        """
        Keyword Arguments:
        - expr_str : string : latex equations as a newline-separated string
        - lines : list : list of latex equations (string)
        - fpath : pathlike : path to a JSON file containing a list of latex equations
        - auto_init : flag to automatically attempt to initialize/load default equations
        """
        #: init properties
        self._template_vars = None
        #: kwds -> instance config
        self.auto_exec = auto_exec
        self.ns_name = f'{ns_prefix}{ns_name}'
        self._errs = []
        self._fpath: AnyStr = None
        self._lines: DesmosLinesContainer = DesmosLinesContainer()
        self.lines, self.fpath = lines, fpath
        if auto_init is True:
            self.setup(expr_str=expr_str, lines=self.lines,
                       fpath=self.fpath, **kwds)
            if auto_exec is True:  # ! only does anything if auto_init is True.
                #: ! modifies namespace if `auto_exec` is True
                self.exec_pycode()

    def reset_cached(self):
        """reset all cached properties"""
        cached_lines = filter(
            lambda a: all([a.kind == 'data', '_lines' in a.name]),
            inspect.classify_class_attrs(self)
        )
        for clines in cached_lines:
            object.__delattr__(self, clines)

    @property
    def fpath(self):
        return self._fpath
    @fpath.setter
    def fpath(self, new):
        self._fpath = Path(new)

    @property
    def lines(self):
        return self._lines
    @lines.setter
    def lines(self, new):
        if isinstance(new, Container):
            self._lines.lines = DesmosLinesContainer(lines=new)
        elif isinstance(new, DesmosLinesContainer):
            self._lines = new

    @cached_property
    def env(self):
        return self.init_jinja_env()

    def init_jinja_env(self):
        #: initialize environment -> instance
        templates_dir = D2P_Resources \
            .get_package_resources_path() \
            .joinpath('templates')
        env = Environment(autoescape=False, optimized=True,
                          loader=FileSystemLoader(
                              searchpath=[
                                  templates_dir
                              ],
                          ))
        #: get the dictionary of values to use for the environment...
        template_vars = self.calc_pycode_environment()
        self.template_vars = template_vars
        return env

    @property
    def template_vars(self):
        return self._template_vars

    @template_vars.setter
    def template_vars(self, newtemp):
        self._template_vars = newtemp

    def setup(self, expr_str=None, lines=None, fpath=None, reset=False,
              **kwds):
        if reset is True:
            self.lines, self.fpath = None, None
        if fpath is not None:
            self.fpath = Path(fpath)
        if self.fpath is not None:
            self.fpath = DesmosLatexParser.get_fpath(pattern='*'+self.fpath.stem+'*')
        if lines is None:
            lines = self.lines
        if fpath is None and self.fpath is None:
            #: get filepath if needed
            self.fpath = DesmosLatexParser.get_fpath(**kwds)
        if expr_str is not None:
            self.lines = expr_str.split('\n')
        if self.fpath is not None and (self.lines.empty or reset is True):
            self.lines = DesmosLatexParser.read_file(self.fpath)
        if self.lines.empty:
            self.setup(fpath=self.fpath)
        return self.lines

    @property
    def latex_lines(self):
        return self.lines
    @latex_lines.setter
    def latex_lines(self, new):
        self.lines = new

    @cached_property
    def sympy_lines(self):
        """
        >>> DesmosLatexParser(auto_init=True, auto_exec=False).sympy_lines
        [Eq(E(x), 1/(1 + exp(-2*x))), Eq(alpha_{m}, 1), Eq(F(x), E(alpha_{m}*x*(alpha_{m} + 1)))]

        """
        slines = DesmosLinesContainer(lines=[])
        try:
            slines.lines = self.parse2sympy(self.latex_lines)
        except Exception:
            logging.warning(traceback.format_exc())
        finally:
            return slines

    @cached_property
    def pycode_lines(self):
        dlc_plines = DesmosLinesContainer()
        try:
            plines_raw = self.parse2pycode(self.sympy_lines)
            dlc_plines.lines = DesmosLatexParser.fix_pycode_line(
                plines_raw, from_sympy=False)
        except Exception:
            logging.warning(traceback.format_exc())
        finally:
            return dlc_plines

    @staticmethod
    def fix_pycode_line(pline: Union[List[AnyStr], AnyStr], from_sympy: bool = False, verbosity=logging.ERROR):
        """fix a line after `sympy.pycode(line)`.

        >>> line = '  # Not supported in Python:\\n  # E\\n(E(x) == 1/(1 + math.exp(-2*x)))'
        >>> DesmosLatexParser.fix_pycode_line(line)
        '(E(x) == 1/(1 + math.exp(-2*x)))'

        """
        if isinstance(pline, DesmosLinesContainer):
            pline = pline.lines
        if isinstance(pline, list):
            plines = [DesmosLatexParser.fix_pycode_line(pl) for pl in pline]
            if isinstance(plines[0], list):
                return flatten(plines)
            return plines
        try:
            if from_sympy is True:
                pline = pycode(pline)
        except Exception:
            with LoggingContext(logger, level=verbosity) as logctx:
                logging.warning(traceback.format_exc())
        pline = pline \
            .split('# Not supported in Python:\n  #')[-1] \
            .split('\n')[-1]
        return pline

    @classmethod
    def parse2pycode(cls, slines):
        """Get self.pycode_lines (not yet finalized for execution)"""
        #: ! reset temporary (instance-level) errors log
        if isinstance(cls, DesmosLatexParser):
            cls._errs = []
        pcode_lines = []
        for sline in slines:
            try:
                pline = pycode(sline)
            except Exception:
                #: ! on failure, log (line, error_msg) to `self._errs`
                msg = traceback.format_exc()
                logging.warning(msg)
                if isinstance(cls, DesmosLatexParser):
                    cls._errs.append((sline, msg))
                pcode_lines.append(sline)
            else:
                pcode_lines.append(pline)
        return pcode_lines

    def fix_pycode_lines(self, pycode_lines=None) -> List[Dict]:
        """Convert pycode equations (from `self.pycode_lines`) to form a set of informative Dict objects.

        returns : Dict : `fix_dict` with info to populate the jinja2 template.
        """
        if pycode_lines is None:
            pycode_lines = self.pycode_lines
        return self.fix_raw_pycode(self.fix_pycode_line(pycode_lines))

    @staticmethod
    def fix_raw_pycode(line):
        return fix_raw_pycode(line)

    @cached_property
    def constants(self):
        return {
            'pi': GlobalConsts.M_PI
        }

    def calc_pycode_environment(self):
        """setup variables for jinja2 environment"""
        lines_fixed = self.fix_pycode_lines()
        params_fixed = list(
            filter(lambda line: line.get('param_name') != '', lines_fixed))
        params_fixed = sorted(
            params_fixed, key=lambda line: line.get('pycode_fixed'))
        equations_fixed = list(
            filter(lambda line: line.get('func_name') != '', lines_fixed))
        equations_fixed = sorted(
            equations_fixed, key=lambda line: line.get('func_name'))
        constants = self.constants
        #: define constants, parameters locally (for equation-level scope)
        tab4 = '    '
        tab8 = tab4 + tab4
        for j in range(len(equations_fixed)):
            eqn_updated = dict(equations_fixed[j])
            eqn_pycode = eqn_updated['pycode_fixed']
            eqn0, eqn1 = eqn_pycode.split(':\n')
            eqn_new = f'\n{tab8}globals().update(vars(self))\n{tab8}' + \
                (tab8).join([
                    f'{param.get("param_name")} = self.{param.get("param_name")}\n'
                    for param in params_fixed
                ])
            eqn_updated['pycode_fixed'] = eqn0 + ':' + eqn_new + tab4 + eqn1
            equations_fixed[j] = eqn_updated
        return {
            'equations': equations_fixed,
            'parameters': params_fixed,
            'constants': constants,
            'ns_name': self.ns_name,
        }

    @cached_property
    def template(self):
        template = self.env.get_template('desmos_model_ns.pyjinja2')
        return template

    @cached_property
    def pycode_string(self):
        """Finalized pycode string.

        Formatted, ready to `exec(...)` !
        """
        #: render template and return...
        return self.template.render(**self.template_vars)

    @property
    def pycode_fixed(self):
        """alias for `self.pycode_string`"""
        return self.pycode_string

    def get_desmos_ns(self):
        """dummy"""
        pass

    def exec_pycode(self):
        """CAUTION: This function uses `exec(...)`.
        """
        global_dict = dict(globals())
        global_dict.update(vars(GlobalConsts))
        exec(self.pycode_string, global_dict)
        self.get_desmos_ns = lambda *args: global_dict.get('get_desmos_ns')()
        return self.get_desmos_ns()

    @property
    def DesmosModelNS(self):
        """CAUTION: refer to `self.exec_pycode(...)`.
        """
        return self.get_desmos_ns()

    #: default location for user-created model output
    default_output_dir = D2P_Resources \
        .get_user_resources_path() \
        .joinpath('models')

    #: desmos2python output file suffix (executable model python code)
    d2p_suffix = '.d2p.py'
    
    def export_model(self, output_dir: PathLike = None, output_filename: PathLike = None) -> PathLike:
        """save the desmos model code (executable python code) to disk"""
        if output_dir is None:
            output_dir = DesmosLatexParser.default_output_dir
        if output_filename is None:
            output_filename = Path(self.fpath) \
                .with_suffix(DesmosLatexParser.d2p_suffix) \
                .name
        output_path = Path(output_dir).joinpath(output_filename)
        output_path.write_text(self.pycode_string)
        logging.info(f'...wrote to {output_path}')
        return output_path

    @classmethod
    def parse2sympy(cls, lines):
        """Get `self.sympy_lines`"""
        if isinstance(lines, DesmosLinesContainer):
            lines = lines.lines
        parsed_lines = parse_latex_lines2sympy(lines)
        return DesmosLinesContainer(lines=parsed_lines)

    @staticmethod
    def get_fpath(**kwds):
        return get_filepath(**kwds)

    @staticmethod
    def read_file(fpath):
        """read a json-formatted list -> latex eqns."""
        lines = read_latex_lines(fpath, split=True)
        return lines


class PatternsMixIn:

    """helper methods for regex patterns"""
    
    @classmethod
    def subn(cls, string, key='desmos_list', repl_key=None, custom_repl=None):
        if repl_key is None:
            repl_key = key
        p = getattr(cls, f'{key}_pattern')
        if custom_repl is None:
            r = getattr(cls, f'{repl_key}_repl')
        else:
            r = custom_repl
        return re.subn(pattern=p, repl=r, string=string)


class PycodePatterns(PatternsMixIn):

    """Pre-compiled regex patterns for `fix_raw_pycode(...)`.
    """

    #: identify subscripts pattern
    subscript_pattern = re.compile(r'_\{([a-zA-Z0-9]+)\}')
    subscript_repl = r'_\1'

    #: same as above, but with multiple groups
    subscript_grouped_pattern = re.compile(r'_\{([a-zA-Z0-9])([a-zA-Z0-9]+)\}')
    subscript_grouped_repl = r'_{\1}'

    #: ! main template pattern
    main_line_pattern = re.compile(
        r'([a-zA-Z_])\(([a-zA-Z_,\s][a-zA-Z_0-9,\s]*)\)\s=')
    main_line_repl: AnyStr = \
        r'''
def _\1(self, \2):
    return'''

    #: mismatched parentheses
    fix_mismatch_pattern = re.compile(r'(\(+.*(?![)\)]))', flags=re.DOTALL)
    fix_mismatch_repl: AnyStr = r'\1'


def fix_raw_pycode(line: Union[AnyStr, List[AnyStr]], retfull: bool = True) -> Dict:
    """Fix a single line of sympy.pycode output to be useful.

    Example:
    -------

    We start with sympy-produced "pycode",

    >>> line = '(E(x) == 1 + math.exp(-2*x))'
    >>> print(line)
    (E(x) == 1 + math.exp(-2*x))

    ...Then using the `fix_raw_pycode(...)` method,
    we end up with executable python code,

    >>> import json
    >>> fix_raw_pycode(line).get('pycode_fixed')
    'def _E(self, x):\\n    return 1 + np.exp(-2*x)'
    """
    #: lines -> line (! handle list of strings)
    if not isinstance(line, str):
        lines = list(line)
        outlines = list(filter(lambda l: l is not None, [fix_raw_pycode(ll, retfull=retfull) for ll in lines]))
        return outlines
    #: keep original line (! in preparation for `retfull`)
    line0 = str(line)
    #: ! Handle double-equals, leading and following parentheses...
    line = str(line).replace(') == ', ') = ')
    line = line.lstrip('(')[:-1]  # remove first and last parentheses
    line = line.replace('cdot ', 'cdot')  # remove extra spaces for cdot
    #: ! Handle '{', '}' -- namely for subscripted variables/functions
    try:
        line = PycodePatterns.subn(PycodePatterns.subn(line, key='subscript_grouped')[0], key='subscript')[0]
    except IndexError:
        pass
    #: ! convert to actual python (numpy) syntax -- ready for `DesmosLatexParser.DesmosModelNS`
    pycode_fixed = re.sub(pattern=PycodePatterns.main_line_pattern,
                          repl=PycodePatterns.main_line_repl,
                          string=line)
    #: ! replace builtin math -> numpy
    pycode_fixed = pycode_fixed.strip().replace('math.', 'np.')
    #: final replacements...
    param_name, param_value, func_name, func_vectorized = '', '', '', ''
    func_sig, func_args = '', ''
    #: ! Again, ensure replacement of `==` -> `=` for parameters...
    if len(pycode_fixed) < 5 or 'def ' != pycode_fixed[:4]:
        #: for free parameters (in Desmos, sliders)
        pycode_fixed = pycode_fixed.replace('==', '=')
        param_name = pycode_fixed.split(' ')[0]  # name of parameter
        try:
            param_value = pycode_fixed.split(
                '=')[1].strip()  # current value
        except IndexError:
            #: ! handle case in which this is neither a parameter, nor an equation
            logging.warning(traceback.format_exc())
            return None
        try:
            param_value = float(param_value)
        except Exception:
            #: ! handle list-like parameters
            param_value = param_value \
                .replace('[', '') \
                .replace(']', '') \
                .split(', ')
    elif 'def ' == pycode_fixed[:4] and retfull is True:
        #: for functions (formulas/equations)
        func_sig = re.match(PycodePatterns.main_line_pattern, line) \
                     .group() \
                     .split(' ')[0]
        func_name = func_sig \
            .split('(')[0]
        func_args = func_sig \
            .split('(')[1] \
            .split(')')[0] \
            .split(',')
        #: ! also include numpy vectorization for functions
        func_vectorized = \
            f'{func_name} = np.vectorize(self._{func_name}, cache=True, excluded="self")'
    #: ! final fix of any mismatched parentheses
    tmp_result = \
        re.subn(pattern=PycodePatterns.fix_mismatch_pattern,
                repl=PycodePatterns.fix_mismatch_repl,
                string=pycode_fixed)
    if tmp_result is not None:
        if tmp_result[1] > 0:
            pycode_fixed = tmp_result[0]
    if retfull is False:
        return pycode_fixed
    return {
        'original_line': line0,
        'pycode_fixed': pycode_fixed,
        'func_name': func_name,
        'func_sig': func_sig,
        'func_args': func_args,
        'func_vectorized': func_vectorized,
        'param_name': param_name,
        'param_value': param_value,
    }


class SympyPatterns(PatternsMixIn):
    """Regex patterns for latex_lines -> sympy_lines.
    """

    #: identify desmos-style lists
    desmos_list_pattern = \
        re.compile(
            r'([A-Za-z0-9]\_?\{[a-zA-Z0-9]\})\=\\left\[([0-9])\.\.\.([0-9])\\right\]'
        )

    @staticmethod
    def desmos_list_repl(m):
        cols = list(range(int(m.group(2)), int(m.group(3))+1))
        return sp.pycode(sp.Eq(sp.Symbol(m.group(1)), sp.Array(cols)))

    @staticmethod
    def desmos_latex_list_repl(m):
        cols = list(range(int(m.group(2)), int(m.group(3))+1))
        cols = ", \\ ".join([str(c) for c in cols])
        return f'{m.group(1)} = \\left[ {cols}\\right]'

    @staticmethod
    def desmos_itemize_repl(m):
        return r'{} = \begin{{\itemize}}'.format(m.group(1)) + \
            ''.join([r'\item{}\n'.format(i) for i in
                     range(int(m.group(2)), 1+int(m.group(3)))]) +\
            r'\end{{\itemize}}'


def parse_latex_lines2sympy(latex_list, verbosity=logging.ERROR):
    """Parse the given list of latex strings to sympy.

    >>> parse_latex_lines2sympy(read_latex_lines(get_filepath(pattern='ex')))
    [Eq(E(x), 1/(1 + exp(-2*x))), Eq(alpha_{m}, 1), Eq(F(x), E(x*(alpha_{m}*(alpha_{m} + 1))))]

    """
    if isinstance(latex_list, str):
        latex_list = [latex_list, ]
    out_list = []
    latex_queue = Queue(maxsize=len(latex_list))
    for latex_line in latex_list:
        latex_queue.put(latex_line)
    while True:
        line = latex_queue.get_nowait()
        matches = PycodePatterns.subn(line, key='subscript_grouped')
        if matches is not None and matches[1] > 0:
            line = matches[0]
        try:
            out = parse_latex(line) \
                .subs('pi', GlobalConsts.M_PI)
        except Exception:
            with LoggingContext(logger, level=verbosity) as log_ctx:
                logging.warning(traceback.format_exc())
            #: ! replace desmos-style lists with latex lists
            line_repl = SympyPatterns.subn(line, key='desmos_list')
            if line_repl[1] > 0 and line_repl[0] is not None:
                line = line_repl[0]
                out_list.append(line)
        else:
            out_list.append(out)
        finally:
            latex_queue.task_done()
            if latex_queue.empty():
                break
    if len(out_list) == 1:
        return out_list[0]
    return out_list


def read_latex_lines(fpth, split=True):
    """open and read JSON file containing a list of latex strings.
    """
    with open(fpth, 'r') as fp:
        lines = json.load(fp)
    #: ! ignore null values
    lines = [l for l in lines if l is not None]
    if split is True:
        latex_lines = lines
    elif split is False:
        latex_lines = '\n'.join(lines)
    return latex_lines


def get_filepath(pattern='*', fext='json', n=1, **kwds):
    """Get a matching filepath from the resources/latex_json directory.

    search path in order:
    - $HOME/.desmos2python/latex_json/
    - $PREFIX/site-packages/desmos2python/resources/latex_json/
    """
    fpaths = []
    for ldir in [D2P_Resources.get_user_resources_path(),
                 D2P_Resources.get_package_resources_path()]:
        fpths = list(
            ldir.joinpath('latex_json') \
            .rglob(f'*{pattern}.{fext}'
                   .replace('**', '*'))
        )
        fpaths.extend(fpths)
        if len(fpaths) > 0:
            break
    if n == 1:
        #: ! ensure at least one path found.
        assert len(fpaths) >= 1
        return fpaths[0]
    return fpaths


def run_demo(**kwds):
    dlp = DesmosLatexParser(**kwds)
    logging.info('...initialized parser to global variable:\n\t`dlp`')
    return dlp


if __name__ == '__main__':
    import doctest
    doctest.testmod()
