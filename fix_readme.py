"""convert to RST (for pypi)

ref: https://stackoverflow.com/a/74086651/1871569
"""
import os
import re
import logging
import traceback
from urllib.error import URLError


def convert2rst():
    long_description = None
    import pypandoc
    from pypandoc.pandoc_download import download_pandoc
    # see the documentation how to customize the installation path
    # but be aware that you then need to include it in the `PATH`
    try:
        download_pandoc()
        os.system('dpkg -x ./$(ls pandoc*.deb|head -1) pandoc_bin')
    except URLError:
        logging.warning(traceback.format_exc())
    #: convert -> rst
    os.system('./pandoc_bin/usr/bin/pandoc -s README.md -t rst -o README.rst~')
    with open('README.rst~', 'r') as f:
        long_description = f.read()
    pattern = re.compile(
        (r'\W+(TOC)\W+(\.\. raw\:\: html)\W+(\<!-- [\w\W]* --\>([\w\W.]*)'
         r'<!-- markdown-toc end -->)'))
    long_description = \
        re.subn(pattern=pattern, string=long_description, repl=r'')[0]
    with open('README.rst', 'w') as f:
        f.write(long_description)
    os.system('rm README.rst~')
    print('...done with fix_readme.py')


if __name__ == '__main__':
    convert2rst()
