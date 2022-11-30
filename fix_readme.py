"""convert to RST (for pypi)

ref: https://stackoverflow.com/a/74086651/1871569
"""
import traceback
import os


def convert2rst():
    long_description = None
    try:
        import pypandoc
        from pypandoc.pandoc_download import download_pandoc
        # see the documentation how to customize the installation path
        # but be aware that you then need to include it in the `PATH`
        download_pandoc()
        os.system('sudo apt install -qqy ./$(ls pandoc*.deb|head -1)')
        #: convert -> rst
        os.system('pandoc -s README.md -t rst -o README.rst')
    except (IOError, ImportError):
        try:
            long_description = pypandoc.convert_file('README.md', 'rst')
        except Exception:
            long_description = open('README.md').read()
            traceback.print_exc()
            print('...failed to convert README.md to rst!')
            print('...using dummy README.rst.')
        finally:
            with open('README.rst', 'w') as fp:
                fp.write(long_description)
    finally:
        print('...done with fix_readme.py')

if __name__ == '__main__':
    convert2rst()