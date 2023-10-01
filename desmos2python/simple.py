
"""Simple latex parser, TODO: extend to use regrx patterns"""
import numpy as np
import re

class DesmosLatexToPython:
    def __init__(self):
        self.func_map = {
            r'\sin': 'np.sin',
            r'\cos': 'np.cos',
            r'\tan': 'np.tan',
            r'\sqrt': 'np.sqrt'
        }

    def replace_latex_functions(self, latex_str):
        """
        Replace LaTeX functions with their numpy equivalents.
        """
        for latex_func, py_func in self.func_map.items():
            latex_str = latex_str.replace(latex_func, py_func)
        return latex_str

    def convert_latex_to_python(self, latex_str):
        """
        Convert Desmos LaTeX string to executable Python code.
        """
        latex_str = self.replace_latex_functions(latex_str)
        # Replace LaTeX specific syntax to Python specific
        latex_str = re.sub(r'\\left\(', '(', latex_str)
        latex_str = re.sub(r'\\right\)', ')', latex_str)
        return latex_str

if __name__ == "__main__":
    converter = DesmosLatexToPython()
    latex_str = r'y = \sin(x) + \cos(x) + \sqrt(x)'
    python_code = converter.convert_latex_to_python(latex_str)
    print(f"Python code: {python_code}")

    # Execute generated Python code
    x = np.linspace(0, 10, 100)
    exec(f'y = {python_code.split("=")[-1]}')
    print(f"y values: {y[:10]}")  # Print first 10 y-values
```

This example is quite basic and may not cover all edge cases. Note that it assumes that the LaTeX string uses `x` as the variable. Feel free to extend this to be more robust and to handle additional LaTeX syntax.
