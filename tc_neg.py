from bit_vector import *

def tc_neg(a):
    return ~a + bv_from_int(a.width(), 1)

print('tc_neg 1 =', tc_neg(b.bv_from_int(16, 1)))
