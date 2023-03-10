desmos2python
=============

convert Desmos equations to executable Python code

Links
-----

-  `desmos2python (PyPI) <https://pypi.org/project/desmos2python/>`__
-  `Desmos Graphing Caculator <https://desmos.com/calculator>`__

Dependencies
------------

**Build/Dev**

-  ``GNU Make``
-  ``docker``

**Libraries**

*required*

-  pandoc (e.g. ``apt-get install pandoc`` for Debian-based, or
   ``pacman -S pandoc`` for Arch Linux)

*(optional) For headless browser functionality (uses ``selenium``):*

-  ``pyenv``
-  ``libxext6``
-  ``libxt6``
-  ``geckodriver`` and ``firefox``

Compatibility
-------------

-  ``python3.10``

-  NOTE: *working on expanding compatibility…*

-  NOTE: *still a work in progress for sure.*

Helpful tips
------------

*…definitely recommend using a virtual environment, e.g. via docker or
conda.*

Install
-------

From PyPi:
~~~~~~~~~~

``python3 -m pip install desmos2python``

Examples
--------

``DesmosLatexParser`` API Example:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

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

Development
-----------

-  Build locally: ``make build``
-  Testing: ``pytest``
