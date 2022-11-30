import os
import logging
import sys
from pathlib import Path
import unittest
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')

rpath = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(
    __file__)), '..', 'src'))
if rpath not in sys.path:
    sys.path.insert(0, rpath)


class TestDesmosWebSession(unittest.TestCase):
    def testDWS(self):
        from desmos2python import DesmosWebSession
        dws = DesmosWebSession()
        ll = dws.latex_list
        self.assertEqual(True, len(ll) > 0)
        dws.export_latex2json()


class TestDesmos2Python(unittest.TestCase):
    def setUp(self):
        self.dlp, self.dmn = None, None

    def tearDown(self):
        del self.dlp
        del self.dmn

    def testDLP(self):
        from desmos2python import DesmosLatexParser
        dlp = DesmosLatexParser()
        logging.info(dlp.pycode_string)
        dmn = dlp.DesmosModelNS()
        x = np.linspace(0, 24, num=100)
        y = dmn.F(x)
        plt.plot(x, y)
        imfn, expfn = \
            Path(__file__).parent.joinpath('ex.png'), \
            Path(__file__).parent.joinpath('expected_ex.png')
        plt.savefig(str(imfn))
        plt.close()
        logging.info('...saved test output to tests/ex.png')
        logging.debug('comparing saved image to expected...')
        with open(imfn, 'rb') as fp:
            imbytes = fp.read()
        with open(expfn, 'rb') as fp:
            expbytes = fp.read()
        self.assertEqual(expbytes, imbytes)
        x1 = [0.1, 0.3, 0.5, 0.9, 1.0, 2.0, 100.0]
        logging.info('x=', x1)
        y1 = dmn.F(x1)
        logging.info('y = F(x): ', y1)
        self.dlp = dlp
        self.dmn = dmn


if __name__ == '__main__':
    unittest.main()
