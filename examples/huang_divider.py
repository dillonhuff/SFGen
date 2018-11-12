from sfgen.bit_vector import *

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

def huang_square_reciprocal(a):
    a_p = concat(bv_from_int(1, 1), a)

    a_sq = zero_extend(2*a_p.width(), a_p) * zero_extend(2*a_p.width(), a_p)

    one_w = build_one_fp(2*a_sq.width(), 2*a_sq.width() - 1)

    quot = one_w / zero_extend(one_w.width(), a_sq)

    q_shifted = quot << bv_from_int(quot.width(), a_sq.width() - 2)

    #print('shifted q =', q_shifted)

    lzc = leading_zero_count(q_shifted)
    #print('lzc after shift =', lzc.to_int())
    assert(lzc <= bv_from_int(lzc.width(), 2))

    q_reshifted = q_shifted << lzc

    #print('q_reshifted =', q_reshifted)

    #return ReciprocalResult(q_reshifted[a_sq.width() : 2*a_sq.width() - 1], lzc[0:1])
    
    return concat(q_reshifted[a_sq.width() : 2*a_sq.width() - 1], lzc[0:1])

def sub_yh(y_h, y_l):
    m = y_h.width() - 1
    width = 2*m

    y_h_ext = zero_extend(2*m, y_h) << bv_from_int(width, 2*m - y_h.width())

    assert(y_h_ext.get(y_h_ext.width() - 1) == QVB(1))
    
    y_l_ext = zero_extend(2*m, y_l)
    y_diff = y_h_ext - y_l_ext

    assert(y_diff.width() == 2*m)

    return y_diff

def huang_div_normalized(x, y):
    assert(x.width() == y.width())
    assert(x.width() % 2 == 0)

    width = x.width()
    m = width // 2
    y_l = y[0 : m - 2]
    y_h = y[width - m - 1 : width - 1]

    assert(y_l.width() == m - 1)
    assert(y_h.width() == m + 1)
    assert(y_h.get(y_h.width() - 1) == QVB(1))
    
    y_h_2_r_and_exp = lookup_in_table(y_h[0 : y_h.width() - 2], huang_square_reciprocal)

    #assert(y_h_2_r_and_exp.width() == (2*m + 2 + 2))

    y_h2_exp = y_h_2_r_and_exp[0 : 1]
    #y_h2_exp = y_h_2_r_and_exp.exponent

    y_h2r = y_h_2_r_and_exp[y_h_2_r_and_exp.width() - (2*m + 2) : y_h_2_r_and_exp.width() - 1]
    #y_h2r = y_h_2_r_and_exp.reciprocal
    
    y_diff = sub_yh(y_h, y_l)
    prod = zero_extend(2*y_diff.width(), x) * zero_extend(2*y_diff.width(), y_diff)
    prod0 = prod >> bv_from_int(width, y_diff.width() - 2)
    prod1 = prod0[0 : 2*m + 2 - 1]

    assert(prod1.width() == 2*m + 2)
    assert(y_h2r.width() == prod1.width())
    
    final_q = zero_extend(2*prod1.width(), prod1) * zero_extend(2*prod1.width(), y_h2r)
    tbs = top_bits(final_q, 2*m + 2)
    round_bits = tbs[0:1]
    last_bits = top_bits(tbs, 2*m)
    rounded_q = last_bits if round_bits == bv_from_int(2, 0) else last_bits + bv_from_int(2*m, 1)
    return concat(rounded_q, y_h2_exp)

def huang_divide(n_in, d_in):
    assert(n_in.width() == d_in.width())
    assert(n_in.width() % 2 == 0)

    width = n_in.width()
    m = width // 2
    
    n_abs = tc_abs(n_in)
    d_abs = tc_abs(d_in)

    lzd = leading_zero_count(d_abs)
    lzn = leading_zero_count(n_abs)
    d_norm = d_abs << lzd
    n_norm = n_abs << lzn

    x = n_norm
    y = d_norm

    res_norm_with_exp = huang_div_normalized(x, y)

    exp = res_norm_with_exp[0:1]
    res_norm = res_norm_with_exp[2 : res_norm_with_exp.width() - 1]
    
    res = res_norm >> (bv_from_int(width, width) + zero_extend(width, exp) - (lzd - lzn) - bv_from_int(width, 3))

    n_sign = sign_bit(n_in)
    d_sign = sign_bit(d_in)

    assert(res.width() == 2*m)

    out = res if n_sign == d_sign else tc_neg(res)
    return out
