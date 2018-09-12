from bit_vector import *
from divider import *

def test_divide_by_two():
    width = 16
    res = newton_raphson_divide(bv_from_int(width, 10), bv_from_int(width, 2))
    print('res =', res)
    assert(res == bv_from_int(width, 5))

def test_21_divided_by_3():
    width = 16
    res = newton_raphson_divide(bv_from_int(width, 20), bv_from_int(width, 5))
    print('res =', res)
    assert(res == bv_from_int(width, 4))
    
def test_21_divided_by_3():
    width = 16
    res = newton_raphson_divide(bv_from_int(width, 21), bv_from_int(width, 3))
    print('res =', res)
    assert(res == bv_from_int(width, 7))

def test_14_divided_by_6():
    width = 16
    res = newton_raphson_divide(bv_from_int(width, 14), bv_from_int(width, 6))
    print('res =', res)
    assert(res == bv_from_int(width, 2))
    

def test_249_divided_by_18():
    width = 16
    res = newton_raphson_divide(bv_from_int(width, 249), bv_from_int(width, 18))
    print('res =', res)
    assert(res == bv_from_int(width, 249 // 18))
