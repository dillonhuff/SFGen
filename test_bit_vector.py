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
    a = BV([QVB(1), QVB(0)])
    b = BV([QVB(1), QVB(0)])

    assert(a == b)


def test_invert():
    a = BV([QVB(1), QVB(0)])
    correct = BV([QVB(0), QVB(1)])

    print('correct = ', correct.to_string())
    print('a       = ', a.to_string())

    assert(invert(a) == correct)

def test_string_construction():
    a = BV([QVB(1), QVB(0)])
    b = bv("2'b10")

    print( 'a = ', a )
    print( 'b = ', b )
    assert(a == b)

def test_add_1():
    a = bv("2'b10")
    res = a + a

    assert(res == bv("2'b10"))
