from sfgen.bit_vector import *
from examples.cube import *

def test_cube():
    width = 32
    a = bv_from_int(width, 7)
    correct = bv_from_int(width, 7*7*7)

    print('a       =', a)    
    print('correct =', correct)
    print('cube(a) =', cube(a))

    assert(cube(a) == correct)
