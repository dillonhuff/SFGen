from bit_vector import *
from cube import *

def test_cube():
    width = 32
    a = bv_from_int(width, 7)
    correct = bv_from_int(width, 7*7*7)

    print('a =', a)
    assert(cube(a) == correct)
