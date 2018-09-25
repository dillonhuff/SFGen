from bit_vector import *

def high_bit(a):
    return a[a.width() - 1 : a.width() - 1]

def float_multiply(a, b, exp_start, exp_end, mant_start, mant_end):
    assert(isinstance(a, QuadValueBitVector))
    assert(isinstance(b, QuadValueBitVector))    

    assert(a.width() == b.width())
    assert((exp_end - exp_start + 1) + (mant_end - mant_start + 1) + 1 == a.width())

    sign_a = high_bit(a)
    sign_b = high_bit(b)
    result_sign = bv_from_int(1, 0) if sign_a == sign_b else bv_from_int(1, 1)
    r = a[0:a.width() - 2]
    r_signed = concat(result_sign, r)

    out = r_signed
    return out
