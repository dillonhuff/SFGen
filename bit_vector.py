X = 2
Z = 3

class QuadValueBit():
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if (not isinstance(other, QuadValueBit)):
            return False
        return self.value == other.value

    def __ne__(self, other):
        if (not isinstance(other, QuadValueBit)):
            return True
        return not (self == other)
    
    def invert(self):
        if (self.value == 0):
            return QuadValueBit(1)
        elif self.value == 1:
            return QuadValueBit(0)
        elif self.value == X:
            return QuadValueBit(X)
        else:
            return QuadValueBit(Z)

    def to_string(self):
        if (self.value == 0):
            return '0'
        elif self.value == 1:
            return '1'
        elif self.value == X:
            return 'x'
        else:
            return 'z'
        
    def __repr__(self):
        return self.to_string()

QVB = QuadValueBit

class QuadValueBitVector():
    def __init__(self, bits):
        self.bits = bits;

    def to_string(self):
        strn = ''
        for b in self.bits:
            strn += b.to_string()

        return strn

    def __eq__(self, other):
        if (not isinstance(other, QuadValueBitVector)):
            return False
        
        if (len(other.bits) != len(self.bits)):
            return False

        for i in range(0, len(self.bits)):
            if (other.bits[i] != self.bits[i]):
                print( 'bits', i, 'differ' )
                return False
        return True

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()
    
BV = QuadValueBitVector

def twos_complement_absolute_value(bv):
    return plus(invert(bv), BV(bv.length(), 1))

def invert(bv):
    bits = []
    for bit in bv.bits:
        bits.append(bit.invert())

    return BV(bits)
