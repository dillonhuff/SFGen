from sfgen.bit_vector import *

def make_const(a, val):
    out = a + bv_from_int(a.width(), val)
    return out
