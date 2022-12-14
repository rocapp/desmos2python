"""desmos2python pandoc wrapper methods"""
import os


def convert(s, opts=''):
    return os.popen(f"echo '{s}' | pandoc {opts}").read()
