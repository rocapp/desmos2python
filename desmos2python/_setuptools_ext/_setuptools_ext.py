"""_setuptools_ext.py: extensions for setuptools commands.
"""
import logging
import os
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

    ref: https://setuptools.pypa.io/en/latest/build_meta.html#how-to-use-it
    ref: https://github.com/pypa/setuptools/blob/1c3b501535a856838a077d50989a5c019d2db679/setuptools/_distutils/cmd.py#L17
    ref: https://stackoverflow.com/a/1321345/1871569
    """
    def __init__(self, dist):
        super().__init__(dist)
        self.D2P_Resources = None
        self.ftmp = None
        delete_ftmp = not bool(os.getenv("D2P_DEBUG", False)) # delete log file if not set
        ts = datetime.datetime.now().isoformat()
        self._log_obj = {"desmos2python": {"_init-user-resources": {"timestamp": ts, "log": [], }}}
        ts_suffix = ts.split('T')[0] + ".log"
        self.ftmp = tempfile.NamedTemporaryFile(prefix="d2p-init-user-resources", suffix=ts_suffix, mode="a+", delete=delete_ftmp)

    def _log(self, msg):
        self._log_obj['desmos2python']['_init-user-resources']['log'].append(msg)
        logging.info(msg)
        return self._log_obj

    def _init_user_resources(self):
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

    def _run(self):
        """initialize desmos2python package/user-local resources.
        - create the user resources directory if it doesn't exist.
        - symlink package resources to `$HOME/.local/share/desmos2python/` directory.
        """
        self.D2P_Resources = importlib.import_module('desmos2python.utils').D2P_Resources
        self._log("...initialized D2P_Resources.")
        self._init_user_resources()
        self._log("...ran _init_user_resources.")
        self._link_pkg_resources()
        self._log("...ran _link_pkg_resources.")
        self._log("...complete!")
        self._close_log()

    def _close_log(self):
        """write, then close log file"""
        self.ftmp.write(json.dumps(self._log_obj, indent=3))
        self.ftmp.close()  # ! deletes the file without D2P_DEBUG env variable

    def run(self):
        """run the original install build step, then the d2p-specific actions (with logging).
        """
        _install.run(self)
        self._log("..._install stage complete.")
        self._run()


from setuptools import build_meta as _orig

prepare_metadata_for_build_wheel = _orig.prepare_metadata_for_build_wheel
build_sdist = _orig.build_sdist


def run_link_files():
    init_resources_d2p(_orig.Distribution())._run()  # ! run post-install step
    return True


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    output = _orig.build_wheel(wheel_directory, config_settings=config_settings, metadata_directory=metadata_directory)
    run_link_files()
    return output
