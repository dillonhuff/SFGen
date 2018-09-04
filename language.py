from bit_vector import *

class Statement:
    def __init__(self):
        return None

class AssignStmt(Statement):
    def __init__(self, lhs, rhs):
        Statement.__init__(self)
        # assert(isinstance(lhs, Variable))
        # assert(isinstance(rhs, Expression))
        self.lhs = lhs
        self.rhs = rhs

class BlockStmt(Statement):
    def __init__(self, i):
        Statement.__init__(self)
        self.stmts = []

    def add_assign(self, lhs, rhs):
        self.stmts.append(AssignStmt(lhs, rhs))
        print('New # of stmts =', len(self.stmts))

    def get_stmts(self):
        return self.stmts

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
        self.inputs = inputs
        self.output = output
        self.values = {output.get_name() : output}
        self.stmt = BlockStmt(1)

    def return_type(self):
        return self.output.get_type()

    def get(self, valueName):
        return self.values[valueName]

    def add_input(self, name, width):
        assert(not name in self.values)

        v = Variable(name, ArrayType(width))
        self.inputs.append(v)
        self.values[name] = v

    def get_formal_args(self):
        print('Inputs = ', self.inputs)
        return self.inputs

    def set_output(self, name, width):
        assert(not name in self.values)

        v = Variable(name, ArrayType(width))
        self.output = v
        self.values[name] = v

    def get_name(self):
        return self.name

    def add_assign(self, lhs, rhs):
        self.stmt.add_assign(lhs, rhs)

    def get_stmt(self):
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
        return FunctionCall(Function("add_" + str(self.width()), [Variable("in0", self.get_type()), Variable("in1", other.get_type())], Variable("out", self.get_type())), [self, other])
        #return FunctionCall("add_" + str(self.width()), [self, other])
    
class Variable(Expression):
    
    def __init__(self, name, width):
        print('Width name = ', type(width).__name__)
        assert(isinstance(width, ArrayType))
        Expression.__init__(self, width)
        self.name = name

    def get_name(self):
        return self.name

    def to_string(self):
        return "(" + self.name + " : " + str(self.get_type().width()) + ")"

    def __repr__(self):
        return self.to_string()

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

    def get_name(self):
        return self.func.get_name()

    def get_args(self):
        return self.args

    def get_formal_args(self):
        return self.func.get_formal_args()

def const(w, val):
    return Constant(bv_from_int(w, val))

class Simulator:
    def __init__(self, function):
        self.f = function
        self.values = {}

    def evaluate_expression(self, expr):
        if (isinstance(expr, Variable)):
            return self.values[expr.get_name()];
        elif (isinstance(expr, FunctionCall)):
            print('Function name = ', expr.get_name())

            argValues = []
            args = expr.get_args()
            formal_args = expr.get_formal_args()

            print('Args = ', args)
            print('Formal args = ', formal_args)

            assert(len(args) == len(formal_args))

            for i in range(0, len(args)):
                formal_arg = formal_args[i]
                arg_value = self.evaluate_expression(args[i])
                print('Arg', formal_arg.get_name(), ' has value = ', arg_value)
                

            assert(False)
        elif (isinstance(expr, Constant)):
            return expr.get_value()
        else:
            print('Error: Illegal expression type', type(expr).__name__)
            assert(False)

    def set_value(lhs, val):
        assert(isinstance(val, QuadValueBitVector))

        self.values[lhs.get_name()] = val

    def evaluate(self):
        print('# of statements = ', len(self.f.get_stmt().get_stmts()))
        for stmt in self.f.get_stmt().get_stmts():
            if (isinstance(stmt, AssignStmt)):
                lhs = stmt.lhs
                rhs = stmt.rhs
                self.set_value(lhs, self.evaluate_expression(rhs))
            else:
                print('Error: Illegal statement type', type(stmt).__name__)
                assert(False)

    def set_input(self, name, value):
        self.values[name] = value

    def get_output(self, name):
        return self.values[name]
