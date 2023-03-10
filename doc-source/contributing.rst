Overview
---------

.. This file based on https://github.com/PyGithub/PyGithub/blob/master/CONTRIBUTING.md

Install ``pre-commit`` with ``pip`` and install the git hook:

.. prompt:: bash

	python -m pip install pre-commit
	pre-commit install


Coding style
--------------

`formate <https://formate.readthedocs.io>`_ is used for code formatting.

It can be run manually via ``pre-commit``:

.. prompt:: bash

	pre-commit run formate -a


Or, to run the complete autoformatting suite:

.. prompt:: bash

	pre-commit run -a


Automated tests
-------------------

Tests are run with ``pytest``.


To run tests for all Python versions, simply run:

.. prompt:: bash

	pytest
