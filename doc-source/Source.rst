=========================
Downloading source code
=========================

The ``desmos2python`` source code is available on GitHub,
and can be accessed from the following URL: https://github.com/rocapp/desmos2python

If you have ``git`` installed, you can clone the repository with the following command:

.. prompt:: bash

	git clone https://github.com/rocapp/desmos2python

.. parsed-literal::

	Cloning into 'desmos2python'...
	remote: Enumerating objects: 47, done.
	remote: Counting objects: 100% (47/47), done.
	remote: Compressing objects: 100% (41/41), done.
	remote: Total 173 (delta 16), reused 17 (delta 6), pack-reused 126
	Receiving objects: 100% (173/173), 126.56 KiB | 678.00 KiB/s, done.
	Resolving deltas: 100% (66/66), done.

| Alternatively, the code can be downloaded in a 'zip' file by clicking:
| :guilabel:`Clone or download` -->  :guilabel:`Download Zip`

.. figure:: git_download.png
	:alt: Downloading a 'zip' file of the source code.

	Downloading a 'zip' file of the source code


Building from source
-----------------------

The recommended way to build ``desmos2python`` is to use `build`:

.. prompt:: bash

	python -m build

The source and wheel distributions will be in the directory ``dist``.

If you wish, you may also use `pep517.build <https://pypi.org/project/pep517/>`_ or another :pep:`517`-compatible build tool.
