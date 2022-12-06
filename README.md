# desmos2python
convert Desmos equations to executable Python code.

## TOC

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [desmos2python](#desmos2python)
    - [TOC](#toc)
    - [Links](#links)
    - [Notes](#notes)
        - [Dependencies](#dependencies)
        - [Compatibility](#compatibility)
        - [Helpful tips](#helpful-tips)
    - [Install](#install)
    - [Examples](#examples)
        - [`make_latex_parser` high-level API Example:](#make_latex_parser-high-level-api-example)
        - [`DesmosLatexParser` API Example:](#desmoslatexparser-api-example)
- [`file` contains a JSON-formatted list of latex equations](#file-contains-a-json-formatted-list-of-latex-equations)
- [loads the example defined in 'resources/latex_json/ex.json'](#loads-the-example-defined-in-resourceslatex_jsonexjson)
- [`pycode_string` contains the ready-to-eval Desmos model namespace](#pycode_string-contains-the-ready-to-eval-desmos-model-namespace)

<!-- markdown-toc end -->

## Links

- [desmos2python (PyPI)](https://pypi.org/project/desmos2python/)
- [Desmos Graphing Caculator](https://desmos.com/calculator)

## Notes

### Dependencies

**Libraries** (Ubuntu package names)

*(optional) For headless browser functionality (uses `selenium`):*

- `libxext6`
- `libxt6`
- `geckodriver` and `firefox`

### Compatibility

- `python3.8`

NOTE: *working on expanding compatibility...*

### Helpful tips

*...definitely recommend using a virtual environment, e.g. via docker or conda.*

## Install

`python3 -m pip install desmos2python`

## Examples

### `make_latex_parser` high-level API Example:

```python
from desmos2python import make_latex_parser

# loads the example defined in 'resources/latex_json/ex.json'
dlp = make_latex_parser(fpath='ex')

# print the raw latex lines
print(dlp.lines.lines)
# output:
# ['E\\left(x\\right)=\\frac{1}{1+\\exp\\left(-2x\\right)}',
# '\\alpha_{m}=1',
# 'F\\left(x\\right)=E\\left(\\alpha_{m}\\cdot\\left(1+\\alpha_{m}\\right)\\cdot x \\right)']

# print sympy-converted lines
print(dlp.sympy_lines.lines)
# output:
# ['E\\left(x\\right)=\\frac{1}{1+\\exp\\left(-2x\\right)}',
#  '\\alpha_{m}=1',
#  'F\\left(x\\right)=E\\left(\\alpha_{m}\\cdot\\left(1+\\alpha_{m}\\right)\\cdot x \\right)']

# print the rendered template (executable python code)
print(dlp.pycode_string)
# """desmosmodelns namespace definition."""
# 
# class DesmosModelNS(object):
# 
#     def __init__(self, **kwds):
#     
#         self._alpha_m = 1
#     
#         #: ! update parameters on construction
#         if len(kwds) > 0:
#             for k in kwds:
#                 setattr(self, '_'+k if '_' != k[0] else k, kwds.get(k))
#         self.setup_equations()
# 
# 
#     @property
#     def alpha_m(self):
#         return self._alpha_m
#     @alpha_m.setter
#     def alpha_m(self, new):
#         self._alpha_m = new
#         #: ! re-init equations
#         self.setup_equations()
# 
# 
#     def setup_equations(self):
#         #: Define vectorized functions (instance-level)
# 
#         self.E = np.vectorize(self._E, cache=True, excluded="self")
# 
#         self.F = np.vectorize(self._F, cache=True, excluded="self")
# 
# 
#     #: Constants
# 
#     pi = 3.141592653589793
# 
# 
#     #: Parameters:
#     params = tuple(( 'alpha_m', ))
# 
#     #: (Functions) State Equations:
#     output_keys = tuple((
#               
#               'E', 
#             
#               
#               'F', 
#             ))
# 
#     def _E(self, x):
#         globals().update(vars(self))
#         alpha_m = self.alpha_m
#         return 1/(1 + np.exp(-2*x))
# 
#     def _F(self, x):
#         globals().update(vars(self))
#         alpha_m = self.alpha_m
#         return E(alpha_m*x*(alpha_m + 1))
# 
# 
# 
# def get_desmos_ns():
#     return DesmosModelNS
# 

# finally, save the rendered python to disk
# saves to this path by default: `$HOME/.desmos2python/models/ex.d2p.py`
output_path = dlp.export_model()
print(output_path)

```

### `DesmosLatexParser` API Example:

```python
import desmos2python as d2p

# `file` contains a JSON-formatted list of latex equations
# loads the example defined in 'resources/latex_json/ex.json'
dlp = d2p.DesmosLatexParser(file='ex.json')

# `pycode_string` contains the ready-to-eval Desmos model namespace 
print(dlp.pycode_string)

# Instantiate a model namespace
# The attributes define any formulas, parameters from the specified Desmos graph
dmn = dlp.DesmosModelNS()

# for example, evaluate the function E(x) over the domain x=(1, 2, 3)
result = dmn.E([1, 2, 3])
print(result)

# see ./tests for more examples!
```
