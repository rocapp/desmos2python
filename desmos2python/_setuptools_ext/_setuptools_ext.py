"""_setuptools_ext.py: extensions for setuptools commands.
"""
import json
import tempfile
import datetime
import importlib
import distutils.core
from distutils.cmd import Command
from setuptools.command.install import install as _install

__all__ = [
    'init_resources_d2p',
    'd2p_subdirs',
]


#: sub-directories to be created
d2p_subdirs = ['calcState_json',
               'latex_json', 'latex_tex',
               'templates', 'models', 'screenshots']


class init_resources_d2p(_install):
    """custom setuptools command for initializing desmos2python resources.

    ref: https://github.com/pypa/setuptools/blob/1c3b501535a856838a077d50989a5c019d2db679/setuptools/_distutils/cmd.py#L17
    ref: https://stackoverflow.com/a/1321345/1871569
    """
    def __init__(self, dist):
        super().__init__(dist)
        self.D2P_Resources = None

    def _init_user_resources(self):
        ts = datetime.datetime.now().isoformat()
        tsinfo = json.dumps({"desmos2python": {"_init-user-resources": {"timestamp": ts}}})
        ts_suffix = ts.split('T')[0] + ".log"
        with tempfile.NamedTemporaryFile(prefix="d2p-init-user-resources", suffix=ts_suffix, mode="w", delete=False) as ftmp:
            ftmp.write(tsinfo)
        user_path = self.D2P_Resources.get_user_resources_path()
        if not user_path.exists():
            user_path.mkdir()   # ! don't overwrite if path already exists
            assert user_path.resolve().exists() is True
        for subdir in d2p_subdirs:
            subdir_path = user_path \
                .joinpath(subdir)
            if not subdir_path.exists():
                subdir_path.mkdir()  # ! don't overwrite if path already exists
            assert subdir_path.resolve().exists() is True
        return True

    def _link_pkg_resources(self):
        pkg_path = self.D2P_Resources.get_package_resources_path()
        pkg_link = self.D2P_Resources.get_package_resources_link_local()
        if not pkg_link.exists():
            pkg_link.symlink_to(pkg_path, target_is_directory=True)
            assert pkg_link.resolve().exists() is True

    def run(self):
        """initialize desmos2python package/user-local resources.

        - create the user resources directory if it doesn't exist.
        - symlink package resources to `$HOME/.local/share/desmos2python/` directory.
        """
        _install.run(self)
        self.D2P_Resources = importlib.import_module('desmos2python.utils').D2P_Resources
        self._init_user_resources()
        self._link_pkg_resources()
