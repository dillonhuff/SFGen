from sfgen.bit_vector import *

def many_assigns(y):
    a = y + bv_from_int(y.width(), 1)
    a = a * a

    out = a
    return out
