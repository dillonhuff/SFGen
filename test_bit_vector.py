from bit_vector import *

def test_quad_value_bit_1_equals_2():
    a = QuadValueBit(1)
    b = QuadValueBit(2)

    assert(a != b)

def test_quad_value_bit_1_equals_1():
    a = QuadValueBit(1)
    b = QuadValueBit(1)

    assert(a == b)

def test_equals():    
    a = bv_from_list([QVB(1), QVB(0)])
    b = bv_from_list([QVB(1), QVB(0)])

    assert(a == b)


def test_invert():
    a = bv_from_list([QVB(1), QVB(0)])
    correct = bv_from_list([QVB(0), QVB(1)])

    print('correct = ', correct.to_string())
    print('a       = ', a.to_string())

    assert(invert(a) == correct)

def test_get_raw_0():
    a = bv_from_list([QVB(1), QVB(0)])
    assert(a.get(0) == QVB(0))

def test_get_raw_1():
    a = bv_from_list([QVB(1), QVB(0)])
    assert(a.get(1) == QVB(1))
    
def test_string_construction():
    a = bv_from_list([QVB(1), QVB(0)])
    b = bv("2'b10")

    print( 'a = ', a )
    print( 'b = ', b )
    assert(a == b)

def test_get_0():
    a = bv("2'b01")
    assert(a.get(0) == QVB(1))

def test_get_1():
    a = bv("2'b01")
    assert(a.get(1) == QVB(0))
    
def test_add_1():
    a = bv("2'b01")
    res = a + a

    assert(res == bv("2'b10"))

def test_mul_2x1():
    a = bv_from_int(32, 2)
    b = bv_from_int(32, 1)

    assert((a * b) == bv_from_int(32, 2*1))

def test_mul_2x2():
    a = bv_from_int(32, 2)
    b = bv_from_int(32, 2)

    assert((a * b) == bv_from_int(32, 2*2))

def test_mul_2x2():
    a = bv_from_int(32, -2)
    b = bv_from_int(32, 2)

    assert((a * b) == bv_from_int(32, -2*2))
    
def test_shift_left():
    a = bv("4'b1011")
    amount = bv("4'b0010")
    res = bv("4'b1100")

    assert((a << amount) == res)

def test_shift_right():
    a = bv("8'b10110010")
    amount = bv("4'b0101")
    res = bv("8'b00000101")

    assert((a >> amount) == res)
    
