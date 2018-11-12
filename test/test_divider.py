from sfgen.bit_vector import *
from examples.divider import *
from examples.huang_divider import *

def divide_case(f, width, n_int, d_int):
    res = f(bv_from_int(width, n_int), bv_from_int(width, d_int))
    print('res =', res)

    res = huang_divide(bv_from_int(width, n_int), bv_from_int(width, d_int))
    correct_mag = abs(n_int) // abs(d_int)
    sgn_n = n_int >= 0
    sgn_d = d_int >= 0
    correct = correct_mag if sgn_n == sgn_d else -correct_mag

    assert(res == bv_from_int(width, correct))
    
def test_divide_by_two():
    width = 16
    divide_case(newton_raphson_divide, width, 10, 2)

def test_20_divided_by_5():
    width = 16
    res = newton_raphson_divide(bv_from_int(width, 20), bv_from_int(width, 5))
    print('res =', res)
    assert(res == bv_from_int(width, 4))
    
def test_21_divided_by_3():
    width = 16
    res = newton_raphson_divide(bv_from_int(width, 21), bv_from_int(width, 3))
    print('res =', res)
    assert(res == bv_from_int(width, 7))

def test_21_divided_by_m3():
    width = 16
    res = newton_raphson_divide(bv_from_int(width, 21), bv_from_int(width, -3))
    print('res =', res)
    assert(res == bv_from_int(width, -7))
    
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

def test_nr_25_5():
    width = 16
    divide_case(newton_raphson_divide, width, 25, 5)

def test_huang_reciprocal_table():
    m = 3
    y_h = bv("4'b1000")
    res = huang_square_reciprocal(y_h[0:y_h.width() - 2])

    assert(res == bv("10'b1000000000"))

def test_huang_reciprocal_table_1001():
    y_h = bv("4'b1001")
    res = huang_square_reciprocal(y_h[0:y_h.width() - 2])

    #assert(res == ReciprocalResult(bv("8'b11001010"), bv("2'b01")))
    assert(res == concat(bv("8'b11001010"), bv("2'b01")))

def test_huang_reciprocal_table_1111():
    y_h = bv("4'b1111")
    res = huang_square_reciprocal(y_h[0:y_h.width() - 2])

    #assert(res == ReciprocalResult(bv("8'b10010001"), bv("2'b10")))
    assert(res == concat(bv("8'b10010001"), bv("2'b10")))

def test_huang_reciprocal_table_1011():
    y_h = bv("4'b1011")
    res = huang_square_reciprocal(y_h[0:y_h.width() - 2])

    assert(res == concat(bv("8'b10000111"), bv("2'b01")))
    # assert(res.reciprocal == bv("8'b10000111"))
    # assert(res.exponent == bv("2'b01"))
    
def test_huang():
    width = 16
    divide_case(huang_divide, width, 16, 4)
    divide_case(huang_divide, width, 256, 2)
    divide_case(huang_divide, width, 25, 5)

    for n in range(-5, 5):
        for d in range(-5, 5):
            if d != 0:
                divide_case(huang_divide, width, n, d)
