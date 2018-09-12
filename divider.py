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
    return a << leading_zero_count(a) #bv_from_int(a.width(), a.leading_zero_count())

def approximate_reciprocal(b):
    width = b.width()
    approximation_width = 10
    normed = normalize_left(b) #b << leadinbv_from_int(width, b.leading_zero_count())

    top_8 = zero_extend(width, normed[width - approximation_width : width - 1])

    assert(top_8.width() == width)

    one_ext = bv_from_int(2*width, 1 << (2*width - 1))
    top_8_ext = zero_extend(2*width, top_8) #.zero_extend(2*width)
    quote = one_ext / top_8_ext

    print('Quote =', quote)

    sliced_quote = (normalize_left(quote))[quote.width() - width:quote.width() - 1]
    print('Sliced quote =', sliced_quote)

    return sliced_quote

def mul_fp(a, b, decimal_place):
    assert(a.width() == b.width());
    
    width = a.width()
    a_ext = zero_extend(2*width, a) #.zero_extend) #(2*width)
    b_ext = zero_extend(2*width, b) #.zero_extend) #(2*width)
    prod = a_ext * b_ext

    return (prod >> bv_from_int(width, decimal_place))[0:width - 1]

def newton_raphson_divide(ne, de):
    assert(ne.width() == de.width())

    width = ne.width()
    
    n = tc_abs(ne)
    d = tc_abs(de)

    n_sign = sign_bit(n)
    d_sign = sign_bit(d)

    one = bv_from_int(width, 1 << (width - 1))
    lzc = leading_zero_count(d) #d.leading_zero_count()
    normed_d = d << (lzc - bv_from_int(width, 1)) #bv_from_int(width, lzc - 1)

    print('Normalized d =', normed_d)

    n_ext = zero_extend(2*width, n) #, .zero_extend(2*width)

    X = approximate_reciprocal(normed_d)

    print('X0 =', X)    

    X = X + mul_fp(X, one - mul_fp(X, normed_d, width - 1), width - 1)

    print('X1 =', X)
    
    print('X    =', fixed_point_to_float(X, width - 1))
    print('1 / D =', 1.0 / fixed_point_to_float(normed_d, width - 1))

    long_prod = n_ext * zero_extend(2*width, X) #.zero_extend(2*width)

    print('n_ext =', n_ext)
    print('n_ext*d =', long_prod)

    widthBV = bv_from_int(width, width)
    res_shift = widthBV + widthBV - (lzc - bv_from_int(width, 1)) - bv_from_int(width, 2)
    print('res_shift =', res_shift)
    shifted_prod = (long_prod >> res_shift)[0:width - 1]
    print('shifted_prod =', shifted_prod)

    q = shifted_prod if normed_d != bv_from_int(width, 1 << (width - 2)) else n >> (widthBV - lzc - bv_from_int(width, 1))

    out = q if d_sign == n_sign else tc_neg(q)

    return out
