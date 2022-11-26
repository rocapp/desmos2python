"""utils.py
"""
import importlib
import sys
import os
from pathlib import Path
from typing import AnyStr, Iterable, List, Union
import logging
import traceback

__all__ = [
    'flatten', 'flatten_list', 'flatten_nested_list',
]


def flatten(l):
    """flatten nested list.

    ref: https://stackoverflow.com/a/952952/1871569
    """
    return [item for sublist in l for item in sublist]
flatten_list = flatten
flatten_nested_list = flatten
