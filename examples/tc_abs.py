from bit_vector import *

def tc_neg(v):
    return ~v + bv_from_int(v.width(), 1)

def tc_is_neg(a):
    return a[a.width() - 1:a.width() - 1] == bv_from_int(1, 1)

def tc_abs(a):
    return tc_neg(a) if tc_is_neg(a) else a

print('tc_abs(9) =', tc_abs(bv_from_int(16, 9)))
print('tc_abs(-9) =', tc_abs(bv_from_int(16, -9)))
