from bit_vector import *

def tc_neg(a):
    return ~a + bv_from_int(a.width(), 1)

def sign_bit(v):
    return v[v.width() - 1:v.width() - 1]

def tc_is_neg(a):
    return a[a.width() - 1:a.width() - 1] == bv_from_int(1, 1)

def tc_abs(a):
    return tc_neg(a) if tc_is_neg(a) else a

def normalize_left(a):
    return a << leading_zero_count(a)

def build_one_fp(width, dist):
    return bv_from_int(width, 1) << bv_from_int(width, dist)

def compute_reciprocal(b):
    width = b.width()
    normed = normalize_left(b)

    top_8 = normed

    assert(top_8.width() == width)

    one_ext = build_one_fp(2*width, 2*width - 1)
    top_8_ext = zero_extend(2*width, top_8)
    quote = one_ext / top_8_ext

    print('Quote =', quote)

    sliced_quote = (normalize_left(quote))[quote.width() - width:quote.width() - 1]

    return sliced_quote
    
def mul_fp(a, b, decimal_place):
    assert(a.width() == b.width());
    
    width = a.width()
    a_ext = zero_extend(2*width, a)
    b_ext = zero_extend(2*width, b)
    prod = a_ext * b_ext

    print('Full precision product =', prod)

    shifted_prod = prod >> bv_from_int(width, decimal_place)

    print('shifted_prod           =', shifted_prod)

    sliced_prod = shifted_prod[0:width - 1]

    print('sliced_prod            =', sliced_prod)

    return sliced_prod

def huang_div_normalized(x, y):
    assert(x.width() == y.width())
    assert(x.width() % 2 == 0)

    print('x norm =', x)
    print('y norm =', y)
    
    width = x.width()
    m = width // 2

    y_l = y[0 : m - 2]
    y_h = y[width - m - 1 : width - 1]

    print('y_h =', y_h)
    print('y_l =', y_l)

    assert(y_l.width() == m - 1)
    assert(y_h.width() == m + 1)

    print('y_h float   =', fixed_point_to_float(y_h, m))
    print('y_h_2 comp  =', fixed_point_to_float(y_h, m) * fixed_point_to_float(y_h, m))

    y_h_2 = mul_fp(y_h, y_h, m)

    print('y_h_2 float =', fixed_point_to_float(y_h_2, m))

    y_h_2_r = compute_reciprocal(y_h_2)

    print('y_h_2_r       =', y_h_2_r)
    print('y_h_2_r float =', fixed_point_to_float(y_h_2_r, m) / 2.0)
    print('y_h_2_r comp  =', 1 / (fixed_point_to_float(y_h, m) * fixed_point_to_float(y_h, m)))

    # Compute X * (Y_h - Y_l)
    y_h_ext = zero_extend(width, y_h) << bv_from_int(width, (m - 1))
    y_l_ext = zero_extend(width, y_l)

    print('y_h_ext =', y_h_ext)
    print('y_l_ext =', y_l_ext)

    y_diff = y_h_ext - y_l_ext

    print('x      =', x)
    print('y_diff =', y_diff)
    
    prod = mul_fp(x, y_diff, width)

    print('prod =', prod)

    # Final multiply
    #y_h_2_r_ext = zero_extend(width, y_h_2_r) << bv_from_int(width, (m + 1))
    y_h_2_r_ext = zero_extend(width, y_h_2_r) << bv_from_int(width, m - 1)
    print('y_h_2_r_ext = ', y_h_2_r_ext)
    final_q = mul_fp(prod, y_h_2_r_ext, width - 1)

    print('Final q       =', final_q)
    
    x_flt = fixed_point_to_float(x, width - 1)
    y_flt = fixed_point_to_float(y, width - 1)

    print('x abs as float =', x_flt)
    print('y abs as float =', y_flt)
    
    print('Final q float =', fixed_point_to_float(final_q, width - 1))
    print('Final q comp  =', x_flt / y_flt)

    # Final shift by exponent?

    return final_q

def huang_divide(n_in, d_in):
    assert(n_in.width() == d_in.width())
    assert(n_in.width() % 2 == 0)

    width = n_in.width()
    m = width // 2
    
    n_abs = tc_abs(n_in)
    d_abs = tc_abs(d_in)

    print('n_abs =', n_abs)
    print('d_abs =', d_abs)

    lzd = leading_zero_count(d_abs)
    lzn = leading_zero_count(n_abs)
    d_norm = d_abs << lzd #normalize_left(d_abs)
    n_norm = n_abs << lzn #normalize_left(n_abs)

    print('n_norm =', n_norm)
    print('d_norm =', d_norm)

    x = n_norm
    y = d_norm

    res_norm = huang_div_normalized(x, y)

    print('lzd =', lzd.to_int())
    print('lzn =', lzn.to_int())
    print('res_norm =', res_norm)

#    res = res_norm >> (bv_from_int(width, width) - (lzd - lzn) - bv_from_int(width, 1))

    res = res_norm >> (bv_from_int(width, width) - (lzd - lzn) - bv_from_int(width, 2))
    n_sign = sign_bit(n_in)
    d_sign = sign_bit(d_in)

    return res if n_sign == d_sign else tc_neg(res)
