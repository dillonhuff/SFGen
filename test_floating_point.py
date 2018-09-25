from bit_vector import *
from floating_point import *

import struct

def binary(num):
    return bin(struct.unpack('!i',struct.pack('!f', num))[0])
    #return ''.join(bin(ord(c)).replace('0b', '').rjust(8, '0') for c in struct.pack('!f', num))

def floatToBits(f):
    s = struct.pack('>f', f)
    val = struct.unpack('>l', s)[0]
    return bv_from_int(32, val)


def test_mul_2_3():
    a = -2.0
    b = 3.0

    print('binary =', floatToBits(a))
    print('binary =', floatToBits(b))
    
    correct = a * b
    res = float_multiply(a, b)

    assert(res == bv_from_float(correct))
