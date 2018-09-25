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
    assert(float_from_bv(bv_from_float(a)) == a)
