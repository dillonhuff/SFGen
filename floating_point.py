from bit_vector import *

def high_bit(a):
    return a[a.width() - 1 : a.width() - 1]

def float_multiply(a, b, exp_start, exp_end, mant_start, mant_end, exp_bias):
    assert(isinstance(a, QuadValueBitVector))
    assert(isinstance(b, QuadValueBitVector))    

    assert(a.width() == b.width())

    exp_width = exp_end - exp_start + 1
    assert(exp_width + (mant_end - mant_start + 1) + 1 == a.width())

    # Tentative exponent computation
    
    a_exp = a[exp_start : exp_end]
    b_exp = b[exp_start : exp_end]

    tentative = (a_exp + b_exp) - bv_from_int(exp_width, exp_bias)
    exp_result = tentative

    # Sign bit computation
    sign_a = high_bit(a)
    sign_b = high_bit(b)
    result_sign = bv_from_int(1, 0) if sign_a == sign_b else bv_from_int(1, 1)
    r = a[mant_start : mant_end]
    r_exp = concat(exp_result, r)
    r_signed = concat(result_sign, r_exp)

    out = r_signed
    return out
