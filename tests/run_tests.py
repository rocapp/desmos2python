import os
import sys
rpath = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
if rpath not in sys.path:
    sys.path.insert(0, rpath)
import numpy as np
import matplotlib
matplotlib.use('qtagg')
import matplotlib.pyplot as plt


def testDLP():
    import desmos2python as d2p
    dlp = d2p.DesmosLatexParser()
    print(dlp.pycode_string)
    dmn = dlp.DesmosModelNS()
    x = np.linspace(0, 24, num=100)
    y = dmn.F(x)
    plt.plot(x, y)
    plt.show()
    plt.savefig(os.path.join(rpath, 'tests/ex.png'))
    plt.close()
    x1 = [0.1, 0.3, 0.5, 0.9, 1.0, 2.0, 100.0]
    print('x=', x1)
    y1 = dmn.F(x1)
    print('y = F(x): ', y1)
    return dlp, dmn


if __name__=='__main__':
    dlp, dmn = testDLP()
