from sfgen.bit_vector import *
from examples.floating_point import *
import random

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
    
def test_double_mul_large_and_complicated():
    a = -234.13087877343224
    b = 9834.230498130842842088
    
    a_bv = bv_from_double(a)
    b_bv = bv_from_double(b)

    r = float_multiply(a_bv, b_bv, 52, 62, 0, 51, 1023)
    
    print('r       =', r)
    print('correct =', bv_from_double(a*b))

    assert(double_from_bv(r) == a * b)


def test_mul_by_zero():
    z = 0.0
    b = 123.0;

    z_bv = bv_from_double(z)
    b_bv = bv_from_double(b)

    res = float_multiply(z_bv, b_bv, 52, 62, 0, 51, 1023)
    assert(double_from_bv(res) == z)

    res = float_multiply(b_bv, z_bv, 52, 62, 0, 51, 1023)
    assert(double_from_bv(res) == z)
    
# def test_mul_subnormal():
#     z_exp = bv_from_int(11, 0)
#     a_s = bv_from_int(52, 1 << 51)
#     b_s = bv_from_int(52, 1 << 51)

#     s = bv_from_int(1, 0)
#     a_bv = concat(concat(s, z_exp), a_s)
#     b_bv = concat(concat(s, z_exp), b_s)

#     print('a_bv =', a_bv)
#     print('b_bv =', b_bv)

#     a = double_from_bv(a_bv)
#     b = double_from_bv(b_bv)

#     assert(bv_from_double(a) == a_bv)
#     assert(bv_from_double(b) == b_bv)

#     print('a   =', a)
#     print('b   =', b)
#     print('a*b =', a*b)

#     r = float_multiply(a_bv, b_bv, 52, 62, 0, 51, 1023)

#     print('r       =', r)
#     print('correct =', bv_from_double(a*b))
    
#     assert(double_from_bv(r) == a * b)
    
def test_random():
    for i in range(0, 10):
        a = random.uniform(-1e-40, 1e40)
        b = random.uniform(-1e-40, 1e40)
        a_bv = bv_from_double(a)
        b_bv = bv_from_double(b)

        print('a =', a)
        print('b =', b)
        
        r = float_multiply(a_bv, b_bv, 52, 62, 0, 51, 1023)

        print('r       =', r)
        print('correct =', bv_from_double(a*b))
        
        assert(double_from_bv(r) == a*b)

