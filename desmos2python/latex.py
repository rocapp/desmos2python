import logging
logger = logging.getLogger(__name__)
from ._logger import LoggingContext
import json
import re
import traceback
from typing import AnyStr, List
from pathlib import Path
from functools import cached_property
import numpy as np
import sympy as sp
from sympy.utilities.lambdify import implemented_function
from sympy.parsing.latex import parse_latex
from sympy import pycode
from sympy.solvers.solveset import nonlinsolve
from jinja2 import Environment, PackageLoader
from .consts import GlobalConsts
import builtins
builtins.__dict__.update(vars(GlobalConsts))


class DesmosLatexParser(object):

    """Helper class for parsing Desmos LaTeX equations.
    """

    def __init__(self, expr_str : AnyStr = None, lines: List[AnyStr] = None,
                 fpath : AnyStr = None, auto_init : bool = True, auto_exec: bool = True,
                 ns_prefix : AnyStr = '', ns_name : AnyStr = 'DesmosModelNS', **kwds):
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
        self.fpath : AnyStr = fpath
        self.lines : List = lines
        if auto_init is True:
            self.setup(expr_str=expr_str, lines=self.lines, fpath=self.fpath, **kwds)
        if auto_exec is True:
            self.exec_pycode()  # ! modifies namespace if `auto_exec` is True

    @cached_property
    def env(self):
        return self.init_jinja_env()

    def init_jinja_env(self):
        #: initialize environment -> instance
        env = Environment(autoescape=False, optimized=True,
                          loader=PackageLoader('desmos2python'))
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

    def setup(self, expr_str=None, lines=None, fpath=None, **kwds):
        self.env  # ! init cached property
        if expr_str is not None:
            self.lines = expr_str.split('\n')
            return
        if fpath is not None:
            self.lines = DesmosLatexParser.read_file(self.fpath)
            return
        #: get filepath if needed
        self.fpath = DesmosLatexParser.get_fpath(**kwds)
        self.setup(fpath=self.fpath)
        return

    @cached_property
    def sympy_lines(self):
        return self.parse2sympy()

    @cached_property
    def pycode_lines(self):
        return self.parse2pycode()

    @property
    def syms(self):
        """get all symbols"""
        return sp.symbols(' '.join(list(set([a.lhs.name for a in self.expr.args]))))

    @property
    def expr(self):
        expr = sp.Expr(*self.sympy_lines)
        subs_dict = {'E': self.sympy_lines[0].rhs, 'pi': GlobalConsts.M_PI}
        for a in expr.args:
            if hasattr(a, 'rhs'):
                if isinstance(a.rhs, float):
                    subs_dict[a.lhs.name] = a.rhs
        expr_out = expr \
            .subs(subs_dict) \
            .simplify()
        return expr_out

    @property
    def system(self):
        """lambdified system of equations"""
        expr = self.expr.replace(
            lambda arg: arg.is_Equality,
            lambda arg: implemented_function(arg.lhs.name, arg.rhs)
        )
        system_lamb = sp.lambdify(self.syms, expr, modules=['scipy', 'numpy'],
                                  cse=True, dummify=True)
        return system_lamb

    @property
    def soln(self):
        return self.solve()

    def solve(self):
        return nonlinsolve(self.sympy_lines, self.syms)

    def parse2pycode(self, slines=None):
        """Get self.pycode_lines (not yet finalized for execution)"""
        if slines is None:
            slines = self.sympy_lines
        #: ! reset temporary (instance-level) errors log
        self._errs = []
        pcode_lines = []
        for sline in slines:
            try:
                pline = pycode(sline)
            except:
                #: ! on failure, log (line, error_msg) to `self._errs`
                msg = traceback.format_exc()
                logging.warning(msg)
                self._errs.append((sline, msg))
            else:
                pline = pline \
                    .split('# Not supported in Python:\n  #')[-1] \
                    .split('\n')[-1]
                pcode_lines.append(pline)
        return pcode_lines

    def fix_pycode_lines(self):
        lines_fixed = [fix_raw_pycode(line) for line in self.pycode_lines]
        return lines_fixed

    @property
    def constants(self):
        return {
            'pi': GlobalConsts.M_PI
        }

    def calc_pycode_environment(self):
        """setup variables for jinja2 environment"""
        lines_fixed = self.fix_pycode_lines()
        params_fixed = list(filter(lambda line: line.get('param_name')!='', lines_fixed))
        params_fixed = sorted(params_fixed, key=lambda line: line.get('pycode_fixed'))
        equations_fixed = list(filter(lambda line: line.get('func_name')!='', lines_fixed))
        equations_fixed = sorted(equations_fixed, key=lambda line: line.get('func_name'))
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

    def parse2sympy(self, lines=None):
        """Get `self.sympy_lines`"""
        if lines is None:
            lines = self.lines
        parsed_lines = parse_latex_lines2sympy(lines)
        sympy_lines = sp.factor_terms(parsed_lines)
        return sympy_lines

    @staticmethod
    def get_fpath(**kwds):
        return get_filepath(**kwds)

    @staticmethod
    def read_file(fpath):
        lines = read_latex_lines(fpath, split=True)
        return lines


def fix_raw_pycode(line: AnyStr, retfull=True):
    """Fix a single line of sympy.pycode output to be useful.

    Example:
    -------
    ```python
        >>> line = 'E(x) = 1 + math.exp(-2*x)'

        >>> line_fixed = fix_raw_pycode(line)

        >>> print(line_fixed)
            def E(x):
                return 1 + np.exp(-2*x)
    ```
    """
    #: keep original line (retfull)
    line0 = str(line)
    #: handle double-equals, leading and following parentheses...
    line = str(line).replace(') == ', ') = ')
    line = line.lstrip('(')[:-1]
    line = line.replace('cdot ', 'cdot')
    #: handle '{', '}'
    line = re.sub(pattern=r'_\{([a-zA-Z0-9]+)\}', repl=r'_\1', string=line)
    #: do regex...
    main_line_pattern = re.compile(r'([a-zA-Z_])\(([a-zA-Z_,\s][a-zA-Z_0-9,\s]*)\)\s=')
    pycode_fixed = re.sub(
        pattern=main_line_pattern,
        repl=r'''
def _\1(self, \2):
    return''',
        string=line
    )
    #: ! replace builtin math -> numpy
    pycode_fixed = pycode_fixed.strip().replace('math.', 'np.')
    param_name, param_value, func_name, func_vectorized = '', '', '', ''
    func_sig, func_args = '', ''
    #: ! finally, replace `==` -> `=` for parameters...
    if len(pycode_fixed) < 5 or 'def ' != pycode_fixed[:4]:
        pycode_fixed = pycode_fixed.replace('==', '=')
        param_name = pycode_fixed.split(' ')[0]
        param_value = float(pycode_fixed.split('=')[1].strip())
    elif 'def ' == pycode_fixed[:4] and retfull is True:
        #: ! also include numpy vectorization for functions
        func_sig = re.match(main_line_pattern, line).group().split(' ')[0]
        func_name = func_sig.split('(')[0]
        func_args = func_sig.split('(')[1].split(')')[0].split(',')
        func_vectorized = f'{func_name} = np.vectorize(self._{func_name}, cache=True, excluded="self")'
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


def parse_latex_lines2sympy(latex_list, verbosity=logging.ERROR):
    """parse the given list of latex strings to sympy"""
    out_list = []
    with LoggingContext(logger, level=verbosity):
        for line in latex_list:
            try:
                out = parse_latex(line).subs('pi', np.pi)
            except:
                logging.warning(traceback.format_exc())
            else:
                out_list.append(out)
    return out_list


def read_latex_lines(fpth, split=True):
    """open and read JSON file containing a list of latex strings."""
    with open(fpth, 'r') as fp:
        lines = json.load(fp)
    if split is True:
        latex_lines = lines
    elif split is False:
        latex_lines = '\n'.join(lines)
    return latex_lines


def get_filepath(pattern='*', fext='json', n=1, **kwds):
    """get a matching filepath from the resources directory"""
    fpaths = list(
        Path(__file__) \
        .parent \
        .parent \
        .rglob(f'*{pattern}.{fext}'.replace('**','*'))
    )
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
