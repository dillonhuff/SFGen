from bit_vector import *
from utils import *

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

class PrintStmt(Statement):
    def __init__(self, print_str, args):
        assert(isinstance(print_str, str))

        Statement.__init__(self)
        self.print_str = print_str
        self.args = args

class BlockStmt(Statement):
    def __init__(self, i):
        Statement.__init__(self)
        self.stmts = []

    def add_assign(self, lhs, rhs):
        assert(isinstance(rhs, Expression))

        self.stmts.append(AssignStmt(lhs, rhs))
        #print('New # of stmts =', len(self.stmts))

    def add_printout(self, print_str, args):
        self.stmts.append(PrintStmt(print_str, args))
        
    def get_stmts(self):
        return self.stmts

class Type:
    def __init__(self):
        return None

class IntegerType(Type):
    def __init__(self):
        Type.__init__(self)

    def __eq__(self, other):
        return isinstance(other, IntegerType)

    def to_string(self):
        return 'Z'

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

class ArrayType(Type):
    def __init__(self, w):
        Type.__init__(self)
        self.w = w

    def __eq__(self, other):
        if (not isinstance(other, ArrayType)):
            return False
        return self.w == other.w

    def width(self):
        return self.w

    def to_string(self):
        return '[' + str(self.w) + ']'

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()
    
class Function:
    def __init__(self, name, inputs, output):
        self.name = name
        self.inputs = inputs
        self.output = output
        self.values = {output.get_name() : output}
        self.stmt = BlockStmt(1)
        self.unique_num = 0

    def return_type(self):
        return self.output.get_type()

    def return_name(self):
        return self.output.get_name()
    
    def var(self, name, width):
        assert(not name in self.values)
        v = Variable(name, ArrayType(width))
        self.values[name] = v
        return v

    def unique_var(self, tp):
        v = Variable("uv_" + str(self.unique_num), tp)
        self.unique_num += 1
        return v

    def get(self, value_name):
        assert(value_name in self.values)
        return self.values[value_name]

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

    def printout(self, print_str, args):
        self.stmt.add_printout(print_str, args)

    def asg(self, rhs):
        lhs = self.unique_var(rhs.get_type())
        self.add_assign(lhs, rhs)
        return lhs

    def get_stmt(self):
        return self.stmt

def new_function(name, out):
    return Function(name, [], out)


class Expression:
    def __init__(self, tp):
        self.tp = tp

    def get_type(self):
        return self.tp

    def bits(self, end, start):
        out_width = end - start + 1
        return FunctionCall(Function("bits_" + str(end) + "_" + str(start),
                                     [Variable("in", self.get_type())],
                                     Variable("out", ArrayType(out_width))),
                            [self])

    def width(self):
        assert(isinstance(self.tp, ArrayType))
        return self.tp.width()

    def __getitem__(self, item):
        return FunctionCall(Function("bits_" + str(item.start) + "_" + str(item.stop), [Variable("in", self.get_type())], Variable("out", self.get_type())), [self])

    def __invert__(self):
        return FunctionCall(Function("invert_" + str(self.width()), [Variable("in", self.get_type())], Variable("out", self.get_type())), [self])

    def __neg__(self):
        return FunctionCall(Function("neg_" + str(self.width()), [Variable("in", self.get_type())], Variable("out", self.get_type())), [self])
    
    def __sub__(self, other):
        return FunctionCall(Function("sub_" + str(self.width()), [Variable("in0", self.get_type()), Variable("in1", other.get_type())], Variable("out", self.get_type())), [self, other])

    def __truediv__(self, other):
        return FunctionCall(Function("unsigned_divide_" + str(self.width()), [Variable("in0", self.get_type()), Variable("in1", other.get_type())], Variable("out", self.get_type())), [self, other])

    def __lshift__(self, other):
        return FunctionCall(Function("shl_" + str(self.width()), [Variable("in0", self.get_type()), Variable("in1", other.get_type())], Variable("out", self.get_type())), [self, other])

    def __rshift__(self, other):
        return FunctionCall(Function("lshr_" + str(self.width()), [Variable("in0", self.get_type()), Variable("in1", other.get_type())], Variable("out", self.get_type())), [self, other])
    
    def __add__(self, other):
        return FunctionCall(Function("add_" + str(self.width()), [Variable("in0", self.get_type()), Variable("in1", other.get_type())], Variable("out", self.get_type())), [self, other])

    def __mul__(self, other):
        return FunctionCall(Function("mul_" + str(self.width()), [Variable("in0", self.get_type()), Variable("in1", other.get_type())], Variable("out", self.get_type())), [self, other])

    #return FunctionCall("add_" + str(self.width()), [self, other])
    
class Variable(Expression):
    
    def __init__(self, name, width):
        #print('Width name = ', type(width).__name__)
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

    def get_value(self):
        return self.value

class FunctionCall(Expression):
    def __init__(self, func, args):
        Expression.__init__(self, func.return_type())
        self.func = func
        self.args = args

    def get_name(self):
        return self.func.get_name()

    def get_args(self):
        return self.args

    def get_func(self):
        return self.func

    def get_formal_args(self):
        return self.func.get_formal_args()

class CaseExpression(Expression):
    def __init__(self, switch_cond, results):
        assert(len(results) > 0)
        Expression.__init__(self, results[0][1].get_type())
        self.switch_cond = switch_cond
        self.results = results
        
    def condition(self):
        return self.switch_cond

    def get_cases(self):
        return self.results

def case_tf(cond, true_res, false_res):
    print('Cond =', cond)
    assert(isinstance(cond, Expression))
    assert(isinstance(true_res, Expression))
    assert(isinstance(false_res, Expression))

    results = [(bv("1'b0"), false_res), (bv("1'b1"), true_res)]
    return CaseExpression(cond, results)
    
def const(w, val):
    return Constant(bv_from_int(w, val))

class Simulator:
    def __init__(self, function):
        self.f = function
        self.values = {}

    def is_builtin(self, name):
        if (has_prefix(name, "invert_")):
            return True

        if (has_prefix(name, "zero_extend_")):
            return True
        
        if (has_prefix(name, "lead_zero_count_")):
            return True
        
        if (has_prefix(name, "equals_")):
            return True
        
        if (has_prefix(name, "add_")):
            return True

        if (has_prefix(name, "unsigned_divide_")):
            return True
        
        if (has_prefix(name, "sub_")):
            return True

        if (has_prefix(name, "mul_")):
            return True
        
        if (has_prefix(name, "shl_")):
            return True

        if (has_prefix(name, "lshr_")):
            return True
        
        if (has_prefix(name, "neg_")):
            return True
        
        if (has_prefix(name, "bits_")):
            return True
        
        return False

    def evaluate_builtin_function(self, f, args):
        name = f.get_name();
        if (has_prefix(name, "invert_")):
            assert(len(args) == 1);
            arg = args[0]
            return invert(arg)

        if (has_prefix(name, "neg_")):
            assert(len(args) == 1);
            arg = args[0]
            return -(arg)

        if (has_prefix(name, "lead_zero_count_")):
            assert(len(args) == 1);
            arg = args[0]
            return bv_from_int(arg.width(), arg.leading_zero_count())
        
        if (has_prefix(name, "add_")):
            assert(len(args) == 2);
            in0 = args[0]
            in1 = args[1]
            return in0 + in1

        if (has_prefix(name, "mul_")):
            assert(len(args) == 2);
            in0 = args[0]
            in1 = args[1]
            return in0 * in1
        
        if (has_prefix(name, "shl_")):
            assert(len(args) == 2);
            in0 = args[0]
            in1 = args[1]
            return in0 << in1

        if (has_prefix(name, "lshr_")):
            assert(len(args) == 2);
            in0 = args[0]
            in1 = args[1]
            return in0 >> in1;
        
        if (has_prefix(name, "unsigned_divide_")):
            assert(len(args) == 2);
            in0 = args[0]
            in1 = args[1]
            return in0 / in1
        
        if (has_prefix(name, "sub_")):
            assert(len(args) == 2);
            in0 = args[0]
            in1 = args[1]
            return in0 - in1
        
        if (has_prefix(name, "equals_")):
            assert(len(args) == 2);
            in0 = args[0]
            in1 = args[1]
            print('Checking if', in0, '==', in1)
            return bv_from_int(1, 1 if in0 == in1 else 0)

        if (has_prefix(name, "zero_extend_")):
            assert(len(args) == 1)
            in0 = args[0]

            print('Zext name =', name)
            m = re.match(r'zero_extend_((\d)*)', name)
            assert(m)
            end_n = m.group(1)

            print('end_n zext =', end_n)

            return in0.zero_extend(int(end_n))
        
        if (has_prefix(name, "bits_")):
            assert(len(args) == 1)
            in0 = args[0]

            m = re.match(r'bits_((\d)*)_((\d)*)', name)
            print('slice name =', name)
            end_n = m.group(1)
            start_n = m.group(3)

            print('end_n   =', end_n)
            print('start_n =', start_n)

            end = int(start_n)
            start = int(end_n)

            return in0.slice_bits(end, start)
        
        else:
            if len(f.stmt().get_stmts()) == 0:
                print('Error: Unsupported builtin: ', f.get_name())
                assert(False)
            else:
                print('Error: Unsupported custom function: ', f.get_name())
                assert(False)

    def evaluate_expression(self, expr):
        #print('Evaluating ', expr)
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

            arg_values = []
            for i in range(0, len(args)):
                formal_arg = formal_args[i]
                arg_value = self.evaluate_expression(args[i])
                print('Arg', formal_arg.get_name(), ' has value = ', arg_value)
                arg_values.append(arg_value)

            if (self.is_builtin(expr.get_name())):
                return self.evaluate_builtin_function(expr, arg_values)
            else:
                if len(expr.get_func().stmt.get_stmts()) != 0:
                    sim = Simulator(expr.get_func())
                    for i in range(0, len(arg_values)):
                        arg_val = arg_values[i]
                        sim.set_input(formal_args[i].get_name(), arg_val)

                    print('Evaluating =', expr.get_func().get_name())
                    print('With expr  =', expr.get_name())
                    sim.evaluate()
                    print('Done evaluating', expr.get_func().get_name())
                    return sim.get_output(expr.get_func().return_name())
                else:
                    print('Error: Unsupported custom function: ', expr.get_name())
                    assert(False)

        elif (isinstance(expr, Constant)):
            return expr.get_value()
        elif (isinstance(expr, CaseExpression)):
            val = self.evaluate_expression(expr.condition())
            for case in expr.get_cases():
                if (case[0] == val):
                    print('case[0] =', case[0])
                    print('val     =', val)
                    return self.evaluate_expression(case[1])

            print('Error: No matching case for', val)
            assert(False)
        else:
            print('Error: Illegal expression type', type(expr).__name__)
            assert(False)

        assert(False)

    def set_value(self, lhs, val):
        assert(isinstance(val, QuadValueBitVector))

        self.values[lhs.get_name()] = val

    def evaluate(self):
        print('# of statements = ', len(self.f.get_stmt().get_stmts()))
        for stmt in self.f.get_stmt().get_stmts():
            if (isinstance(stmt, AssignStmt)):
                lhs = stmt.lhs
                rhs = stmt.rhs
                self.set_value(lhs, self.evaluate_expression(rhs))
            elif (isinstance(stmt, PrintStmt)):
                pstr = stmt.print_str
                res_str = ''
                i = 0
                arg_ind = 0
                while i < len(pstr):
                    ci = pstr[i]
                    if ci != '%':
                        res_str += ci
                        i += 1
                    elif pstr[(i + 1)] == 'b':
                        arg = stmt.args[0]
                        arg_ind += 1
                        i += 2
                        res_str += self.evaluate_expression(arg).to_string()
                    else:
                        print('Error: Unsupported format directive', ci, 'in', pstr)
                        assert(False)

                print(res_str)
            else:
                print('Error: Illegal statement type', type(stmt).__name__)
                assert(False)

    def set_input(self, name, value):
        assert(isinstance(name, str))
        self.values[name] = value

    def get_output(self, name):
        return self.values[name]

def unop(func, arg):
    return FunctionCall(func, [arg])

def eq(a, b):
    assert(isinstance(a, Expression))
    assert(isinstance(b, Expression))

    return FunctionCall(Function("equals_" + str(a.width()),
                                 [Variable("in0", ArrayType(a.width())),
                                  Variable("in1", ArrayType(b.width()))],
                                 Variable("out", ArrayType(1))),
                        [a, b])

def lead_zero_count(a):
    assert(isinstance(a, Expression))

    return FunctionCall(Function("lead_zero_count_" + str(a.width()),
                                 [Variable("in", ArrayType(a.width()))],
                                 Variable("out", ArrayType(a.width()))),
                        [a])

def zero_extend(w, a):
    assert(isinstance(w, int))
    assert(isinstance(a, Expression))

    return FunctionCall(Function("zero_extend_" + str(w),
                                 [Variable("in", ArrayType(a.width()))],
                                 Variable("out", ArrayType(w))),
                        [a])
