from bit_vector import *

def tc_neg(a):
    return ~a + bv_from_int(a.width(), 1)

def sign_bit(v):
    return v[v.width() - 1:v.width() - 1]

def tc_is_neg(a):
    return a[a.width() - 1:a.width() - 1] == bv_from_int(1, 1)

def tc_abs(a):
    return tc_neg(a) if tc_is_neg(a) else a

def newton_raphson_divide(ne, de):
    n = tc_abs(ne)
    d = tc_abs(de)

    n_sign = sign_bit(n)
    d_sign = sign_bit(d)

    q = n / d

    out = q if d_sign == n_sign else tc_neg(q)

    return out
