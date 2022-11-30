import numpy as np
import builtins


class GlobalConst:

    """Global constants:
    """

    #: a (very) small number
    EPS: float = 1e-13

    #: Conway's constant
    CONWAY: float = 1.303577269034296391257099112152551890730702504659404875754861390628550

    #: Pi^4
    PI4: float = 97.40909103400243723644033268870511124972758567268542169146785938997085

    #: Dirichlet L(4,chi) [ ref : https://tinyurl.com/dirichletL4 ]
    DIRL4: float = PI4 / 96.0

    #: sqrt(2) (1.4142135623730951...)
    SQRT2 = np.sqrt(2.0)
    
    #: Gieseking-Konstante (1.0149416064096537...)
    GIEKONST = 1.01494160640965362502

    #: Phi (golden ratio)
    PHI = 1.61803398874989484820458683436563811772030917980576286213544862270526046281890244970720720418939113748475

    #: GCNO scale constant
    GCNO = 2.77

    M_PI = np.pi


#: alias
GlobalConsts = GlobalConst

"""Global consts -> global namespace:
"""
builtins.__dict__.update(vars(GlobalConsts))
