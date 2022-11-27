import os
import logging
import sys
import unittest
rpath = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
if rpath not in sys.path:
    sys.path.insert(0, rpath)

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


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
        plt.savefig(os.path.join(rpath, 'tests/ex.png'))
        plt.close()
        logging.info('...saved test output to tests/ex.png')
        x1 = [0.1, 0.3, 0.5, 0.9, 1.0, 2.0, 100.0]
        logging.info('x=', x1)
        y1 = dmn.F(x1)
        logging.info('y = F(x): ', y1)
        self.dlp = dlp
        self.dmn = dmn


if __name__=='__main__':
    unittest.main()
