# desmos2python
convert Desmos equations to executable Python code.

*NOTE: This is very much a work in progress.*

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

**Build/Dev**

- `GNU Make`
- `docker`

**Libraries**

*required*

- pandoc (e.g. `apt-get install pandoc` for Debian-based, or `pacman -S pandoc` for Arch Linux)

*(optional) For headless browser functionality (uses `selenium`):*

- `pyenv`
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

## Development

- Build locally: `make build`
- Testing: `tox -e`
