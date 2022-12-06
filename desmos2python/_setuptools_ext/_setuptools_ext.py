"""_setuptools_ext.py: extensions for setuptools commands.
"""
from distutils.cmd import Command
from desmos2python.utils import D2P_Resources

__all__ = [
    'init_resources_d2p',
]


class init_resources_d2p(Command):
    """custom setuptools command for initializing desmos2python resources.

    ref: https://github.com/pypa/setuptools/blob/1c3b501535a856838a077d50989a5c019d2db679/setuptools/_distutils/cmd.py#L17
    """

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def _init_user_resources(self):
        user_path = D2P_Resources.get_user_resources_path()
        if not user_path.exists():
            user_path.mkdir()
            assert user_path.resolve().exists() is True
            for subdir in ['latex_json', 'templates', 'models']:
                subdir_path = user_path \
                    .joinpath(subdir)
                subdir_path.mkdir()
                assert subdir_path.resolve().exists() is True

    def _link_pkg_resources(self):
        pkg_path = D2P_Resources.get_package_resources_path()
        pkg_link = D2P_Resources.get_package_resources_link_local()
        if not pkg_link.exists():
            pkg_link.symlink_to(pkg_path, target_is_directory=True)
            assert pkg_link.resolve().exists() is True

    def run(self):
        """initialize desmos2python package/user-local resources.

        - create the user resources directory if it doesn't exist.
        - symlink package resources to `$HOME/.local/share/desmos2python/` directory.
        """
        self._init_user_resources()
        self._link_pkg_resources()

