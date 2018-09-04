from bit_vector import *

class Expression:
    def __init__(self, bit_width):
        self.bit_width = bit_width

    def width(self):
        return self.bit_width

    def __invert__(self):
        return FunctionCall("invert_", [self])

    def __add__(self, other):
        return Binop("add", self, other)
    
class Variable(Expression):
    def __init__(self, name, width):
        Expression.__init__(self, width)
        self.name = name

class Constant(Expression):
    def __init__(self, bv):
        assert(isinstance(bv, QuadValueBitVector))
        Expression.__init__(self, bv.width())
        self.value = bv

class FunctionCall(Expression):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Negate(Expression):
    def __init__(self, op0):
        self.op0 = op0

class Binop(Expression):
    def __init__(self, name, op0, op1):
        self.name = name
        self.op0 = op0
        self.op1 = op1
        
class Statement:
    def __init(self):
        self.stmts = []

    def add_assign(self, lhs, rhs):
        return None

def const(w, val):
    return Constant(bv_from_int(w, val))

class Function:
    def __init__(self, name):
        self.name = name
        self.inputs = {}
        self.outputs = {}
        self.values = {}

    def get(self, valueName):
        return self.values[valueName]

    def add_input(self, name, width):
        v = Variable(name, width)
        self.inputs[name] = v
        self.values[name] = v

    def add_output(self, name, width):
        v = Variable(name, width)
        self.outputs[name] = v
        self.values[name] = v

    def stmt(self):
        return Statement()

def new_function(name):
    return Function(name)

class Simulator:
    def __init__(self, function):
        self.f = function
        self.values = {}

    def evaluate(self):
        
        return None

    def set_input(self, name, value):
        self.values[name] = value

    def get_output(self, name):
        return self.values[name]
