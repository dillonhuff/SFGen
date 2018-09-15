from bit_vector import *

def top_bits(b, num_bits):
    return b[b.width() - num_bits : b.width() - 1]

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

def huang_square_reciprocal(a):
    a_p = concat(bv_from_int(1, 1), a)
    print('a_p =', a_p)

    #a_sq = mul_fp(a_p, a_p, a_p.width() - 1)
    a_sq = zero_extend(2*a_p.width(), a_p) * zero_extend(2*a_p.width(), a_p)

    print('a_sq =', a_sq)

    one_w = build_one_fp(2*a_sq.width(), 2*a_sq.width() - 1)
    print('one_w =', one_w)

    quot = one_w / zero_extend(one_w.width(), a_sq)
    print('quot =', quot)

    q_shifted = quot << bv_from_int(quot.width(), a_sq.width() - 2)

    print('shifted q =', q_shifted)

    lzc = leading_zero_count(q_shifted)
    print('lzc after shift =', lzc.to_int())
    assert(lzc <= bv_from_int(lzc.width(), 2))

    q_reshifted = q_shifted << lzc

    print('q_reshifted =', q_reshifted)
    
    return concat(q_reshifted[a_sq.width() : 2*a_sq.width() - 1], lzc[0:1])

def sub_yh(y_h, y_l):
    m = y_h.width() - 1
    width = 2*m

    y_h_ext = zero_extend(2*m, y_h) << bv_from_int(width, 2*m - y_h.width())

    print('y_h_ext =', y_h_ext)

    assert(y_h_ext.get(y_h_ext.width() - 1) == QVB(1))
    
    y_l_ext = zero_extend(2*m, y_l)
    y_diff = y_h_ext - y_l_ext

    assert(y_diff.width() == 2*m)

    return y_diff

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

    assert(y_h.get(y_h.width() - 1) == QVB(1))
    
    y_h_2_r_and_exp = huang_square_reciprocal(y_h[0 : y_h.width() - 2])

    print('y_h_2_r_and_exp       =', y_h_2_r_and_exp)
    print('y_h_2_r_and_exp width =', y_h_2_r_and_exp.width())
    assert(y_h_2_r_and_exp.width() == (2*m + 2 + 2))

    y_h2_exp = y_h_2_r_and_exp[y_h_2_r_and_exp.width() - 2 : y_h_2_r_and_exp.width() - 1]
    y_h2r = y_h_2_r_and_exp[y_h_2_r_and_exp.width() - (2*m + 2) : y_h_2_r_and_exp.width() - 1]

    print('y_h2r     =', y_h2r)
    print('y_h2_exp =', y_h2_exp)

    print('y_h_2_r float =', fixed_point_to_float(y_h2r, y_h2r.width() - 1))
    print('y_h_2_r comp  =', 1 / (fixed_point_to_float(y_h, m) * fixed_point_to_float(y_h, m)))

    y_diff = sub_yh(y_h, y_l)

    prod = zero_extend(2*y_diff.width(), x) * zero_extend(2*y_diff.width(), y_diff)

    #x_ext = zero_extend(2*m, x) << bv_from_int(width, 2)
    #print('x_ext  =', x_ext)
    #prod = mul_fp(x_ext, y_diff, 2*m + 2 - 1)

    print('x*y_diff =', prod)

    prod = prod >> bv_from_int(width, y_diff.width() - 2)
    prod = prod[0 : 2*m + 2 - 1]

    print('Rounded prod =', prod)

    assert(prod.width() == 2*m + 2)

    # Final multiply
    print('y_h2r width = ', y_h2r.width())
    assert(y_h2r.width() == prod.width())
    
    #    final_q = mul_fp(prod, y_h2r, y_h2r.width() - 1)
    final_q = zero_extend(2*prod.width(), prod) * zero_extend(2*prod.width(), y_h2r)

    print('Final q       =', final_q)

    # Now need to shift and round up.

    # x_flt = fixed_point_to_float(x, width - 1)
    # y_flt = fixed_point_to_float(y, width - 1)

    # print('x abs as float =', x_flt)
    # print('y abs as float =', y_flt)
    
    # print('Final q float =', fixed_point_to_float(final_q, width - 1))
    # print('Final q comp  =', x_flt / y_flt)

    tbs = top_bits(final_q, 2*m + 2)
    round_bits = tbs[0:1]
    last_bits = top_bits(tbs, 2*m)
    
    rounded_q = last_bits if round_bits == bv("2'b00") else last_bits + bv_from_int(2*m, 1)
        

    #rounded_q = (final_q >> bv_from_int(width, 2))[0:final_q.width() - 3]

    print('rounded_q =', rounded_q)

    return concat(rounded_q, y_h2_exp)

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
    d_norm = d_abs << lzd
    n_norm = n_abs << lzn

    # print('n_norm =', n_norm)
    # print('d_norm =', d_norm)

    x = n_norm
    y = d_norm

    res_norm_with_exp = huang_div_normalized(x, y)

    exp = res_norm_with_exp[0:1]
    res_norm = res_norm_with_exp[2 : res_norm_with_exp.width() - 1]

    # print('lzd =', lzd.to_int())
    # print('lzn =', lzn.to_int())
    print('res_norm =', res_norm)
    print('res_exp  =', exp)

    

#    shift_dist = bv_from_int(width, width) + zero_extend(width, exp) - (lzd - lzn) - bv_from_int(width, 3)

    res = res_norm >> (bv_from_int(width, width) + zero_extend(width, exp) - (lzd - lzn) - bv_from_int(width, 4))
    n_sign = sign_bit(n_in)
    d_sign = sign_bit(d_in)
    #    res = res_norm >> (bv_from_int(width, width) + zero_extend(width, exp) - (lzd - lzn) - bv_from_int(width, 3))
    assert(res.width() == 2*m)

    return res if n_sign == d_sign else tc_neg(res)
