"""desmos2python pandoc wrapper methods"""
import os
import pypandoc as pdoc


def convert2html(s, opts=''):
    """convert generic input (e.g., latex) to pandoc HTML format"""
    return os.popen(f"echo '{s}' | pandoc {opts}").read()


def convert2plain(estr, clean_ws=True):
    """convert generic input (e.g., latex) to pandoc plain format"""
    plain = pdoc.convert_text(source=estr, to='plain', format='latex')
    if clean_ws is True:
        plain = plain.strip().replace('\n', '').replace('\r', '')
    return plain
