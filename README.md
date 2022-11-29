# desmos2python
seamless conversion between Desmos LaTeX equations &amp; executable Python code.

## Example:

```python

import desmos2python as d2p

# `file` contains a JSON-formatted list of latex equations
# By default, loads the example defined in 'resources/latex_json/ex.json'
dlp = d2p.DesmosLatexParser(file=...)

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
