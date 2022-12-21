import json
import pandas as pd
from desmos2python.utils import D2P_Resources


class GreekAlphabet:

    """Namespace for accessing the greek alphabet as (name, unicode symbol).

    ref: https://gist.githubusercontent.com/beniwohli/765262/raw/68980c0e2135777db9bd7cfdf1eea365dc8c68f9/greek_alphabet.py
    """
    
    def __init__(self):
        self.rpath = D2P_Resources.get_package_resources_link_local()
        self.d = json.loads(self.rpath.joinpath('greek_alphabet.json').read_text())
        #: access like: GreekAlphabet().df['Alpha'], output: 'A'
        self.df = pd.Series(self.d) \
                    .to_frame() \
                    .reset_index(names=['uni']) \
                    .set_index(0).T

    def get(self, name, as_item=True):
        if as_item is True:
            return self.df[name].item()
        return self.df[name]

    def get_from_unicode(self, uni):
        cols = [c for c in self.df.columns if self.df[c].item() == uni]
        if len(cols) == 0:
            raise RuntimeError(
                f"no greek character matching given name: '{uni}'")
        return cols[0]
