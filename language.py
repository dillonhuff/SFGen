from bit_vector import *

class Type:
    def __init__(self):
        return None

class ArrayType(Type):
    def __init__(self, w):
        self.w = w

    def width(self):
        return self.w

class Function:
    def __init__(self, name, inputs, output):
        self.name = name
        self.inputs = []
        self.output = output
        self.values = {output.get_name() : output}
        self.stmt = BlockStmt

    def return_type(self):
        return self.output.get_type()

    def get(self, valueName):
        return self.values[valueName]

    def add_input(self, name, width):
        assert(not name in self.values)

        v = Variable(name, ArrayType(width))
        self.inputs.append(v)
        self.values[name] = v

    def set_output(self, name, width):
        assert(not name in self.values)

        v = Variable(name, ArrayType(width))
        self.output = v
        self.values[name] = v

    def stmt(self):
        return self.stmt

def new_function(name, out):
    return Function(name, [], out)


class Expression:
    def __init__(self, tp):
        self.tp = tp

    def get_type(self):
        return self.tp

    def width(self):
        assert(isinstance(self.tp, ArrayType))
        return self.tp.width()

    def __invert__(self):
        return FunctionCall(Function("invert_" + str(self.width()), [Variable("in", self.get_type())], Variable("out", self.get_type())), [self])

    def __add__(self, other):
        return FunctionCall(Function("add_" + str(self.width()), [Variable("in0", self.get_type()), Variable("in1", other.get_type())], Variable("out", self.get_type())), [self])
        #return FunctionCall("add_" + str(self.width()), [self, other])
    
class Variable(Expression):
    
    def __init__(self, name, width):
        print('Width name = ', type(width).__name__)
        assert(isinstance(width, ArrayType))
        Expression.__init__(self, width)
        self.name = name

    def get_name(self):
        return self.name

class Constant(Expression):
    def __init__(self, bv):
        assert(isinstance(bv, QuadValueBitVector))
        Expression.__init__(self, ArrayType(bv.width()))
        self.value = bv

class FunctionCall(Expression):
    def __init__(self, func, args):
        Expression.__init__(self, func.return_type())
        self.func = func
        self.args = args

class Statement:
    def __init__(self):
        return None

class AssignStmt(Statement):
    def __init__(self, lhs, rhs):
        Statement.__init__(self)
        assert(isinstance(lhs, Variable))
        assert(isinstance(rhs, Expression))
        self.lhs = lhs
        self.rhs = rhs

class BlockStmt(Statement):
    def __init__(self):
        Statement.__init__(self)
        self.stmts = []

    def add_assign(self, lhs, rhs):
        self.stmts.append(AssignStmt(lhs, rhs))

def const(w, val):
    return Constant(bv_from_int(w, val))

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
