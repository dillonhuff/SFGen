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
    assert(ne.width() == de.width())

    width = ne.width()
    
    n = tc_abs(ne)
    d = tc_abs(de)

    n_sign = sign_bit(n)
    d_sign = sign_bit(d)

    one = bv_from_int(2*width, 1 << (2*width - 1))
    lzc = d.leading_zero_count()
    normed_d = d << bv_from_int(width, lzc - 1)

    print('Normalized d =', normed_d)

    ext_d = normed_d.zero_extend(2*width)

    # Approximate one / D
    d_ = one / ext_d
    print('d_ =', d_)
    n_ext = n.zero_extend(2*width)


    long_prod = n_ext * d_
    print('n_ext =', n_ext)
    print('n_ext*d =', long_prod)

    res_shift = width + width - (lzc - 1) - 2
    print('res_shift =', res_shift)
    shifted_prod = (long_prod >> bv_from_int(width, res_shift))[0:width - 1]
    print('shifted_prod =', shifted_prod)
    
    q = n / d

    out = q if d_sign == n_sign else tc_neg(q)

    return out
