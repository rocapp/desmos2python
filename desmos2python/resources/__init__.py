import importlib
import logging

__all__ = [
    'GreekAlphabet',
    'greek',
    'convert_greek_chars'
]

#: globally accessible
greek_chars = None
GreekAlphabet = None
greek = None
convert_greek_chars = None
try:
    greek_chars = importlib.import_module('.greek_chars', 'desmos2python.resources')
except ModuleNotFoundError:
    logging.warn("couldn't import greek_chars module.", exc_info=1)
else:
    GreekAlphabet = greek_chars.GreekAlphabet
    greek = greek_chars.greek
    convert_greek_chars = greek_chars.convert_greek_chars