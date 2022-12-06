"""utils.py
"""
from pathlib import Path
import importlib.resources

__all__ = [
    'flatten', 'flatten_list', 'flatten_nested_list',
    'D2P_Resources',
]


def flatten(l):
    """flatten nested list.

    ref: https://stackoverflow.com/a/952952/1871569
    """
    return [item for sublist in l for item in sublist]


#: aliases:
flatten_list = flatten
flatten_nested_list = flatten


class D2P_Resources:

    """Namespace for methods related to desmos2python resources."""
    
    @staticmethod
    def get_user_resources_path():
        """get path to user custom resources (output)"""
        return Path('~').expanduser().joinpath('.desmos2python')

    @staticmethod
    def get_package_resources_link_local():
        """refers to a symlink target (pointing to `$PREFIX/site-packages/desmos2python/resources`)."""
        return Path('~').expanduser().joinpath('.local', 'share', 'desmos2python')

    @staticmethod
    def get_package_resources_path():
        return next(importlib.resources.path("desmos2python.resources", ".").gen)
