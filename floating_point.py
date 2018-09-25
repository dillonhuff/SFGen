from bit_vector import *

def high_bit(a):
    return a[a.width() - 1 : a.width() - 1]

def float_multiply(a, b, exp_start, exp_end, mant_start, mant_end, exp_bias):
    assert(isinstance(a, QuadValueBitVector))
    assert(isinstance(b, QuadValueBitVector))    

    assert(a.width() == b.width())

    exp_width = exp_end - exp_start + 1
    mant_width = mant_end - mant_start + 1    

    assert(exp_width + mant_width + 1 == a.width())

    # Tentative exponent computation
    
    a_exp = a[exp_start : exp_end]
    b_exp = b[exp_start : exp_end]

    tentative = (a_exp + b_exp) - bv_from_int(exp_width, exp_bias)
    exp_result = tentative

    # Mantissa computation
    a_mant = concat(bv_from_int(1, 1), a[mant_start : mant_end])
    b_mant = concat(bv_from_int(1, 1), b[mant_start : mant_end])

    a_mant_ext = zero_extend(2*a_mant.width(), a_mant)
    b_mant_ext = zero_extend(2*a_mant.width(), b_mant)

    prod = a_mant_ext * b_mant_ext

    carry_out = high_bit(prod) == bv_from_int(1, 1)

    prod_shifted = prod >> bv_from_int(a.width(), 1) if carry_out else prod
    exp_shifted = exp_result + bv_from_int(exp_result.width(), 1) if carry_out else exp_result

    print('sigprod         =', prod)
    print('sigprod shifted =', prod_shifted)

    prod_sliced = (prod_shifted >> bv_from_int(a.width(), mant_width))[0 : mant_width - 1]

    print('prod sliced =', prod_sliced)
    
    # Sign bit computation
    sign_a = high_bit(a)
    sign_b = high_bit(b)
    result_sign = bv_from_int(1, 0) if sign_a == sign_b else bv_from_int(1, 1)
    r = prod_sliced #a[mant_start : mant_end]
    r_exp = concat(exp_shifted, r)
    r_signed = concat(result_sign, r_exp)

    out = r_signed
    return out
