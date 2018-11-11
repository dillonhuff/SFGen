from sfgen.bit_vector import *

def high_bit(a):
    return a[a.width() - 1 : a.width() - 1]

def get_bit(a, val):
    return a[val : val]

def float_multiply(a, b, exp_start, exp_end, mant_start, mant_end, exp_bias):
    assert(isinstance(a, QuadValueBitVector))
    assert(isinstance(b, QuadValueBitVector))

    assert(a.width() == b.width())

    exp_width = exp_end - exp_start + 1
    mant_width = mant_end - mant_start + 1    

    assert(exp_width + mant_width + 1 == a.width())

    # Check subnormals
    a_exp = a[exp_start : exp_end]
    b_exp = b[exp_start : exp_end]

    a_is_subnorm = a_exp == bv_from_int(exp_width, 0)
    b_is_subnorm = b_exp == bv_from_int(exp_width, 0)

    # Mantissa computation
    a_mant_tmp = a[mant_start : mant_end]
    b_mant_tmp = b[mant_start : mant_end]

    a_lz = leading_zero_count(a_mant_tmp)
    b_lz = leading_zero_count(b_mant_tmp)

    if a_is_subnorm and a_exp == bv_from_int(exp_width, 0):
        return bv_from_int(a.width(), 0)

    if b_is_subnorm and b_exp == bv_from_int(exp_width, 0):
        return bv_from_int(a.width(), 0)
    
    if a_is_subnorm:
        a_mant_tmp = a_mant_tmp << (a_lz + bv_from_int(a_lz.width(), 1))
        a_exp = bv_from_int(b_exp.width(), 1) - a_lz[0:a_exp.width() - 1]
    if b_is_subnorm:
        b_mant_tmp = a_mant_tmp << (a_lz + bv_from_int(a_lz.width(), 1))
        b_exp = bv_from_int(b_exp.width(), 1) - b_lz[0:a_exp.width() - 1]

    a_mant = concat(bv_from_int(1, 1), a_mant_tmp)
    b_mant = concat(bv_from_int(1, 1), b_mant_tmp)

    print('a subnorm =', a_is_subnorm)
    print('b subnorm =', b_is_subnorm)

    a_mant_ext = zero_extend(2*a_mant.width(), a_mant)
    b_mant_ext = zero_extend(2*a_mant.width(), b_mant)

    print('a_mant_ext =', a_mant_ext)
    print('b_mant_ext =', b_mant_ext)

    print('a_exp =', a_exp)
    print('b_exp =', b_exp)

    # Get tentative exponent
    tentative = (a_exp + b_exp) - bv_from_int(exp_width, exp_bias)
    exp_result = tentative

    # Compute product
    prod = a_mant_ext * b_mant_ext

    carry_out = high_bit(prod) == bv_from_int(1, 1)

    prod_shifted = prod >> bv_from_int(a.width(), 1) if carry_out else prod
    exp_shifted = exp_result + bv_from_int(exp_result.width(), 1) if carry_out else exp_result

    print('sigprod         =', prod)
    print('sigprod shifted =', prod_shifted)

    M0 = zero_extend(2, get_bit(prod_shifted, mant_width))
    R = zero_extend(2, get_bit(prod_shifted, mant_width - 1))
    S = zero_extend(2, orr(prod_shifted[0 : mant_width - 2]))

    print('M0 =', M0)
    print('R  =', R)
    print('S  =', S)
    print('RD =', R*(M0 + S))
    if (R*(M0 + S) != bv_from_int(M0.width(), 0)):
        print('Rounding')
        rounded = bv_from_int(prod_shifted.width(), 1) << bv_from_int(a.width(), 52)

        assert(rounded.width() == prod_shifted.width())
        prod_shifted_rounded = prod_shifted + rounded
    else:
        print('Not rounding')
        prod_shifted_rounded = prod_shifted

    print('Prod shifted rounded =', prod_shifted_rounded)
    prod_sliced = (prod_shifted_rounded >> bv_from_int(a.width(), mant_width))[0 : mant_width - 1]

    print('prod sliced =', prod_sliced)
    
    # Sign bit computation
    sign_a = high_bit(a)
    sign_b = high_bit(b)
    result_sign = bv_from_int(1, 0) if sign_a == sign_b else bv_from_int(1, 1)
    r = prod_sliced
    r_exp = concat(exp_shifted, r)
    r_signed = concat(result_sign, r_exp)

    out = r_signed
    return out
