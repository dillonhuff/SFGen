from bit_vector import *
from floating_point import *

def test_float_conversion_neg():
    a = -2.0
    assert(float_from_bv(bv_from_float(a)) == a)

def test_float_conversion_pos():
    a = 3.0
    assert(float_from_bv(bv_from_float(a)) == a)

def test_float_conversion_complicated():
    a = -23.491
    a_bv = bv_from_float(a)
    res_bv = bv_from_float(float_from_bv(bv_from_float(a)))

    print('a_bv   =', a_bv)
    print('res_bv =', res_bv)

    assert(a_bv == res_bv)

def test_double_conversion_complicated():
    a = -23.491
    a_bv = bv_from_double(a)
    res_bv = bv_from_double(double_from_bv(bv_from_double(a)))

    print('a_bv   =', a_bv)
    print('res_bv =', res_bv)

    assert(a_bv == res_bv)
    assert(double_from_bv(bv_from_double(a)) == a)
    
def test_double_mul_one():
    a = 1.0
    a_bv = bv_from_double(a)

    r = float_multiply(a_bv, a_bv, 52, 62, 0, 51, 1023)

    print('r = ', r)

    assert(double_from_bv(r) == a*a)

def test_double_mul_minus_one():
    a = -1.0
    a_bv = bv_from_double(a)

    r = float_multiply(a_bv, a_bv, 52, 62, 0, 51, 1023)

    print('r = ', r)

    assert(double_from_bv(r) == a*a)


def test_double_mul_mixed_one():
    a = -1.0
    b = 1.0
    
    a_bv = bv_from_double(a)
    b_bv = bv_from_double(b)

    r = float_multiply(a_bv, b_bv, 52, 62, 0, 51, 1023)

    print('r = ', r)

    assert(double_from_bv(r) == a*b)
    
def test_double_mul_powers_of_two():
    a = -8.0
    b = 16.0
    
    a_bv = bv_from_double(a)
    b_bv = bv_from_double(b)

    r = float_multiply(a_bv, b_bv, 52, 62, 0, 51, 1023)
    
    print('r       =', r)
    print('correct =', bv_from_double(a*b))

    assert(double_from_bv(r) == a*b)
    
def test_double_mul_exact_rep():
    a = 12.0
    b = 12.0
    
    a_bv = bv_from_double(a)
    b_bv = bv_from_double(b)

    r = float_multiply(a_bv, b_bv, 52, 62, 0, 51, 1023)
    
    print('r       =', r)
    print('correct =', bv_from_double(a*b))

    assert(double_from_bv(r) == a*b)
    
