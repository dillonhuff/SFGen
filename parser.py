import ast
import language as l
import bit_vector as b
import copy

from utils import *

class LowInstruction:
    def __init__(self):
        return None

    def to_string(self):
        return '\tUNKNOWN_INSTR\n'

    def __repr__(self):
        return self.to_string()

def is_width_call(func):
    return isinstance(func, ast.Attribute) and (func.attr == 'width')

class ITEInstr(LowInstruction):
    def __init__(self, res, test, true_exp, false_exp):
        self.res = res
        self.test = test
        self.true_exp = true_exp
        self.false_exp = false_exp

    def replace_values(self, f):
        self.res = f(self.res)
        self.test = f(self.test)
        self.true_exp = f(self.true_exp)
        self.false_exp = f(self.false_exp)
        
    def used_values(self):
        return {self.res, self.test, self.true_exp, self.false_exp}

    def to_string(self):
        return '\tite {0} {1} {2} {3}\n'.format(self.res, self.test, self.true_exp, self.false_exp)

class SliceInstr(LowInstruction):
    def __init__(self, res, value, low, high):
        self.res = res
        self.value = value
        self.low = low
        self.high = high

    def replace_values(self, f):
        self.res = f(self.res)
        self.value = f(self.value)
        self.low = f(self.low)        
        self.high = f(self.high)                

    def used_values(self):
        return {self.res, self.value, self.low, self.high}
        
    def to_string(self):
        return '\tslice {0} {1} {2} {3}\n'.format(self.res, self.value, self.low, self.high)

class CompareInstr(LowInstruction):
    def __init__(self, op, res, lhs, rhs):
        self.op = op
        self.res = res
        self.lhs = lhs
        self.rhs = rhs

    def used_values(self):
        return {self.res, self.lhs, self.rhs}
        
    def to_string(self):
        return '\tcmp {0} {1} {2}\n'.format(self.res, self.lhs, self.rhs)

    def replace_values(self, f):
        self.res = f(self.res)
        self.lhs = f(self.lhs)
        self.rhs = f(self.rhs)        

class ConstDecl(LowInstruction):
    def __init__(self, res_name, num):
        self.res_name = res_name
        self.num = num

    def replace_values(self, f):
        self.res_name = f(self.res_name)

    def used_values(self):
        return {self.res_name}
        
    def to_string(self):
        return '\tconst ' + self.res_name + ' ' + str(self.num) + '\n'

class ConstBVDecl:
    def __init__(self, res_name, width, val):
        self.res_name = res_name
        self.value = b.bv_from_int(width, val)

    def used_values(self):
        return {self.res_name}
        
    def to_string(self):
        return '\tconstbv ' + self.res_name + ' ' + str(self.value) + '\n'

class AssignInstr(LowInstruction):
    def __init__(self, res, rhs):
        self.res = res
        self.rhs = rhs

    def replace_values(self, f):
        self.res = f(self.res)
        self.rhs = f(self.rhs)
        
    def used_values(self):
        return {self.res, self.rhs}
        
    def to_string(self):
        return '\tassign {0} {1}\n'.format(self.res, self.rhs)

class ReturnInstr(LowInstruction):
    def __init__(self, name):
        self.val_name = name

    def replace_values(self, f):
        self.val_name = f(self.val_name)

    def used_values(self):
        return {self.val_name}
        
    def to_string(self):
        return '\treturn ' + self.val_name + '\n'

class BinopInstr(LowInstruction):
    def __init__(self, op, res, lhs, rhs):
        self.op = op
        self.res = res
        self.lhs = lhs
        self.rhs = rhs

    def replace_values(self, f):
        self.res = f(self.res)
        self.lhs = f(self.lhs)
        self.rhs = f(self.rhs)        
        
    def used_values(self):
        return {self.res, self.lhs, self.rhs}
        
    def to_string(self):
        return '\tbinop ' + str(self.op) + ' ' + self.res + ' ' + self.lhs + ' ' + self.rhs + '\n'

class UnopInstr(LowInstruction):
    def __init__(self, op, res, in_name):
        self.op = op
        self.res = res
        self.in_name = in_name


    def replace_values(self, f):
        self.res = f(self.res)
        self.in_name = f(self.in_name)
        
    def used_values(self):
        return {self.res, self.in_name}
        
    def to_string(self):
        return '\tunop ' + str(self.op) + ' ' + self.res + ' ' + self.in_name + '\n'
        
class CallInstr(LowInstruction):
    def __init__(self, res, func, args):
        self.res = res
        self.func = func
        self.args = args

    def replace_values(self, f):
        self.res = f(self.res)
        new_args = []
        for arg in self.args:
            new_args.append(f(arg))
        self.args = new_args

    def used_values(self):
        s = {self.res}
        for arg in self.args:
            s.add(arg)

        return s
        
    def to_string(self):
        s = '\tcall ' + self.res + ' ' + str(self.func) + ' '
        arg_strs = []
        for a in self.args:
            arg_strs.append(str(a))
        s += comma_list(arg_strs)
        s += '\n'

        return s
        
class LowFunctionDef:
    def __init__(self, name, args):
        self.name = name
        self.args = args
        self.instructions = []
        self.unique_num = 0
        self.symbol_table = {}
        self.output = None
        for arg in args:
            self.symbol_table[arg] = None

    def get_int_constant_value(self, name):
        for instr in self.instructions:
            if isinstance(instr, ConstDecl) and instr.res_name == name:
                return instr.num

        assert(False)
                
    def unique_suffix(self):
        suf = '_us_' + str(self.unique_num)
        self.unique_num += 1
        return suf

    def input_names(self):
        return self.args

    def get_arg(self, ind):
        assert(isinstance(ind, int))
        return self.args[ind]

    def symbol_type(self, name):
        assert(name in self.symbol_table)
        return self.symbol_table[name]
    
    def set_symbol_type(self, name, tp):
        self.symbol_table[name] = tp
    
    def has_symbol(self, name):
        return name in self.symbol_table

    def add_instr(self, instr):
        assert(self.output == None)
        self.instructions.append(instr)
        if (isinstance(instr, ReturnInstr)):
            self.output = instr.val_name

    def output_name(self):
        return self.output

    def add_symbol(self, name, tp):
        self.symbol_table[name] = tp

    def fresh_sym(self):
        name = "fs_" + str(self.unique_num)
        self.unique_num += 1
        self.add_symbol(name, None)
        return name
        
    def to_string(self):
        s = 'symbols\n';
        for sym in self.symbol_table:
            s += '\t' + sym + ' -> ' + str(self.symbol_table[sym]) + '\n'
        s += 'endsymbols\n\n'
        s += 'function ' + self.name + '('
        s += comma_list(self.args) + ')\n'
        for instr in self.instructions:
            s += instr.to_string()
        s += 'end'
        return s

class LowCodeGenerator(ast.NodeVisitor):
    def __init__(self):
        ast.NodeVisitor.__init__(self)
        self.active_function = None
        self.functions = {}
        self.expr_names = {}

    def get_function(self, name):
        assert(name in self.functions)
        return self.functions[name]

    def has_function(self, name):
        return name in self.functions

    def visit_Stmt(self, stmt):

        if isinstance(stmt, ast.Import):
            self.visit_Import(stmt)
        elif isinstance(stmt, ast.ImportFrom):
            self.visit_ImportFrom(stmt)
        elif isinstance(stmt, ast.Assert):
            print('Log: Assert statement', stmt, 'ignored during synthesis')
        elif isinstance(stmt, ast.FunctionDef):
            self.visit_FunctionDef(stmt)
        elif isinstance(stmt, ast.Assign):
            if self.active_function != None:
                assert(len(stmt.targets) == 1)
                self.visit_Expr(stmt.targets[0])
                self.visit_Expr(stmt.value)
                self.active_function.add_instr(AssignInstr(self.expr_name(stmt.targets[0]), self.expr_name(stmt.value)))

        elif isinstance(stmt, ast.Expr):
            if self.active_function == None:
                print('Log: Synthesis ignores top level expression', ast.dump(stmt))
            else:
                print('Expression without statement', ast.dump(stmt))
                if isinstance(stmt.value, ast.Call):
                    print('Call')
                    if isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == 'print':
                        print('Log: Print call ignored by synthesis')
                        return
                assert(False)
        elif isinstance(stmt, ast.Return):
            self.visit_Return(stmt)
        else:
            self.generic_visit(stmt)
        
    def visit_Module(self, node):
        for stmt in node.body:
            self.visit_Stmt(stmt)


    def expr_name(self, expr):
        assert(expr in self.expr_names)
        return self.expr_names[expr]

    def visit_Expr(self, expr):
        assert(self.active_function != None)

        if isinstance(expr, ast.BinOp):
            self.visit_Expr(expr.left)
            self.visit_Expr(expr.right)
            
            lhs = self.expr_name(expr.left)
            rhs = self.expr_name(expr.right)

            res_name = self.active_function.fresh_sym()
            self.active_function.add_instr(BinopInstr(expr.op, res_name, lhs, rhs))
            self.expr_names[expr] = res_name

        elif isinstance(expr, ast.UnaryOp):
            self.visit_Expr(expr.operand)

            in_name = self.expr_name(expr.operand)
            res_name = self.active_function.fresh_sym()
            self.active_function.add_instr(UnopInstr(expr.op, res_name, in_name))
            self.expr_names[expr] = res_name
            
        elif isinstance(expr, ast.Name):
            if not self.active_function.has_symbol(expr.id):
                self.active_function.add_symbol(expr.id, None)
            self.expr_names[expr] = expr.id

        elif isinstance(expr, ast.Call):
            res = self.active_function.fresh_sym()

            if is_width_call(expr.func):
                assert(len(expr.args) == 0)

                # print(ast.dump(expr))
                # assert(False)
                self.visit_Expr(expr.func.value)
                assert(expr.func.attr == 'width')
                res = self.active_function.fresh_sym()

                self.active_function.add_instr(CallInstr(res, 'width', [self.expr_name(expr.func.value)]))
            else:
                arg_exprs = []
                for arg in expr.args:
                    self.visit_Expr(arg)
                    arg_exprs.append(self.expr_name(arg))
                self.active_function.add_instr(CallInstr(res, expr.func, arg_exprs))
            self.expr_names[expr] = res

        elif isinstance(expr, ast.IfExp):
            res = self.active_function.fresh_sym()
            self.visit_Expr(expr.test)
            self.visit_Expr(expr.body)
            self.visit_Expr(expr.orelse)

            self.active_function.add_instr(ITEInstr(res,
                                                    self.expr_name(expr.test),
                                                    self.expr_name(expr.body),
                                                    self.expr_name(expr.orelse)))
            self.expr_names[expr] = res

        elif isinstance(expr, ast.Num):
            n = self.active_function.fresh_sym()
            self.active_function.add_instr(ConstDecl(n, expr.n))
            self.expr_names[expr] = n

        elif isinstance(expr, ast.Compare):
            self.visit_Expr(expr.left)

            assert(len(expr.comparators) == 1)

            self.visit_Expr(expr.comparators[0])
            res = self.active_function.fresh_sym()
            assert(len(expr.ops) == 1)
            self.active_function.add_instr(CompareInstr(expr.ops[0], res, self.expr_name(expr.left), self.expr_name(expr.comparators[0])))
            self.expr_names[expr] = res

        elif isinstance(expr, ast.Subscript):
            self.visit_Expr(expr.value)
            self.visit_Expr(expr.slice.lower)
            self.visit_Expr(expr.slice.upper)

            res = self.active_function.fresh_sym()
            self.active_function.add_instr(SliceInstr(res,
                                                      self.expr_name(expr.value),
                                                      self.expr_name(expr.slice.lower),
                                                      self.expr_name(expr.slice.upper)))
            self.expr_names[expr] = res
            
        else:
            print('Error: Unhandled expression:', ast.dump(expr))
            assert(False)

    def visit_Import(self, node):
        return None

    def visit_ImportFrom(self, node):
        return None
    
    def visit_Return(self, node):
        assert(self.active_function != None)
        
        self.visit_Expr(node.value)
        val_name = self.expr_name(node.value)
        self.active_function.add_instr(ReturnInstr(val_name))

    def visit_FunctionDef(self, node):
        assert(self.active_function == None)


        print('Function def =', node.name)
        arg_names = []
        for arg in node.args.args:
            arg_names.append(arg.arg)
            print(ast.dump(arg))

        fdef = LowFunctionDef(node.name, arg_names)
        self.active_function = fdef

        for stmt in node.body:
            self.visit_Stmt(stmt)

        self.functions[node.name] = fdef

        self.active_function = None

    # def visit_Expr(self, node):
    #     print('Expr =', node.name)

    def generic_visit(self, node):
        print('Error: Unsupported node type', node)
        assert(False)

def swap_instrs(new_func, new_instrs):
    new_func.output = None
    new_func.instructions = []
    for instr in new_instrs:
        new_func.add_instr(instr)

class ScheduleConstraints:
    def __init__(self):
        self.num_cycles = 1

class Schedule:
    def __init__(self):
        self.unique_num = 0
        self.functional_units = {}
        self.total_num_cycles = 0

    def num_cycles(self):
        return self.total_num_cycles

    def get_binding(self, instr):
        for func_name in self.functional_units:
            func = self.functional_units[func_name]
            sched = func[1]
            print('Checking', sched)
            for i in range(0, len(sched)):
                print('i =', i)
                it = sched[i]
                if it == instr:
                    return (func_name, i)
        assert(False)

    def to_string(self):
        s = '--- Schedule\n'
        for unit in self.functional_units:
            s += '\t' + unit + ' -> ' + str(self.functional_units[unit]) + '\n'
        return s

    def bind_instruction(self, unit_name, start_time, instruction):
        unit = self.functional_units[unit_name]
        unit[1].append(instruction)

    def fresh_name(self, prefix):
        n = prefix + '_' + str(self.unique_num)
        self.unique_num += 1
        return n

    def get_functional_units(self):
        units = []
        for unit in self.functional_units:
            units.append((self.functional_units[unit][0],
                          self.functional_units[unit][1],
                          unit))

        return units

    def add_unit(self, unit):
        name = self.fresh_name(unit.name)
        self.functional_units[name] = (unit, [])
        return name

    def num_states(self):
        return 1

    def num_functional_units(self):
        return len(self.functional_units)

class Operation:
    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters

    def __eq__(self, other):
        if not isinstance(other, Operation):
            return False

        if (len(self.parameters) != len(other.parameters)):
            return False

        for i in range(0, len(self.parameters)):
            if self.parameters[i] != other.parameters[i]:
                return False
        return True

def op_string(op):
    if isinstance(op, ast.Invert):
        return 'invert'
    if isinstance(op, ast.Add):
        return 'add'
    if isinstance(op, ast.Eq):
        return 'eq'

    assert(False)

sameWidthOps = [ast.Invert, ast.Add, ast.Sub]

def anyinstance(i, tps):
    for t in tps:
        if isinstance(i, t):
            return True
    return False

def functional_unit(instr, f):
    if isinstance(instr, BinopInstr) or isinstance(instr, UnopInstr):
        name = op_string(instr.op)
        if (anyinstance(instr.op, sameWidthOps)):
            name += '_' + str(16)

        return Operation(name, [16])
    if isinstance(instr, CompareInstr):
        name = op_string(instr.op)
        in_width = f.symbol_type(instr.lhs).width()
        name += '_' + str(in_width)

        return Operation(name, [in_width])
    if isinstance(instr, AssignInstr):
        name = 'assign'
        in_width = f.symbol_type(instr.rhs).width()
        name += '_' + str(in_width)
        return Operation(name, [in_width])

    elif isinstance(instr, ConstBVDecl):
        name = 'constant_' + str(instr.value)
        return Operation(name, [instr.value])
    elif isinstance(instr, CallInstr):
        assert(isinstance(instr.func, ast.Name))
        return Operation(instr.func.id, [])
    elif isinstance(instr, ITEInstr):
        return Operation('ite_' + str(16), [16])
    elif isinstance(instr, SliceInstr):
        high_val = f.get_int_constant_value(instr.high)
        low_val = f.get_int_constant_value(instr.low)
        in_width = f.symbol_type(instr.value).width()
        return Operation('slice_' + str(in_width) + '_' + str(low_val) + '_' + str(high_val), [in_width, low_val, high_val])
    else:
        print('Unsupported functional unit', instr)
        assert(False)

def schedule(code_gen, f, constraints):
    s = Schedule()
    for instr in f.instructions:
        if not isinstance(instr, ReturnInstr) and not isinstance(instr, ConstDecl):
            unit_name = s.add_unit(functional_unit(instr, f))
            s.bind_instruction(unit_name, 0, instr)

    return s

def get_primitives(c):
    if isinstance(c[0], l.Type) and isinstance(c[1], str):
        return (c[1], c[0])
    if isinstance(c[1], l.Type) and isinstance(c[0], str):
        return (c[0], c[1])

    return None

def substitute(name, tp, c):
    if c == name:
        return tp
    else:
        return c

def substitute_constraint(name, tp, c):
    return (substitute(name, tp, c[0]), substitute(name, tp, c[1]))

def unify_types(spec_f):
    f = spec_f
    constraints = []
    int_constants = {}
    for sym in spec_f.symbol_table:
        if spec_f.symbol_type(sym) != None:
            constraints.append((sym, spec_f.symbol_type(sym)))

    for instr in f.instructions:
        if isinstance(instr, UnopInstr):
            res = instr.res
            operand = instr.in_name
            constraints.append((res, operand))
        elif isinstance(instr, BinopInstr):
            res = instr.res
            a = instr.lhs
            b = instr.rhs
            constraints.append((res, a))
            constraints.append((a, b))
        elif isinstance(instr, AssignInstr):
            res = instr.res
            a = instr.rhs
            constraints.append((res, a))
        elif isinstance(instr, ConstDecl):
            int_constants[instr.res_name] = instr.num
        elif isinstance(instr, CompareInstr):
            res = instr.res
            a = instr.lhs
            b = instr.rhs
            constraints.append((res, l.ArrayType(1)))
            constraints.append((a, b))
        elif isinstance(instr, ConstDecl):
            res = instr.res_name
            constraints.append((res, l.IntegerType()))
        elif isinstance(instr, ITEInstr):
            constraints.append((instr.res, instr.true_exp))
            constraints.append((instr.res, instr.false_exp))
            constraints.append((instr.test, l.ArrayType(1)))
        elif isinstance(instr, SliceInstr):
            if (instr.low in int_constants) and (instr.high in int_constants):
                hg = int_constants[instr.high]
                lw = int_constants[instr.low]
                assert(hg >= lw)
                constraints.append((instr.res, l.ArrayType(hg - lw + 1)))
        else:
            print('Error: Cannot unify types in instruction', instr.to_string)

    print('Type constraints')
    for c in constraints:
        print(c)

    resolved = []
    clen = len(constraints)
    while len(resolved) < clen:
        primitives = None
        for ind in range(0, len(constraints)):
            c = constraints[ind]
            primitives = get_primitives(c)
            if primitives != None:
                resolved.append(c)
                print('Resolved', c)
                break


        if primitives == None:
            print('Unresolved constraints =', constraints)
            # Check for contradictions
            for c in constraints:
                if isinstance(c[0], l.Type) and isinstance(c[1], l.Type) and c[0] != c[1]:
                    print('Contradiction in constraints', c)
                    assert(False)

            break
        
        new_constraints = []
        for i in range(0, len(constraints)):
            if i != ind:
                other = constraints[i]
                rs = substitute_constraint(primitives[0], primitives[1], other)
                if rs[0] != rs[1]:
                    new_constraints.append(rs)
        constraints = new_constraints

    # After unifying resolve all calls to widths and replace the results with
    # appropriate constants.

    print('Unified constraints')
    for c in resolved:
        print(c)
        prim = get_primitives(c)
        spec_f.set_symbol_type(prim[0], prim[1])
                    
def get_const_int(name, func):
    for instr in func.instructions:
        if isinstance(instr, ConstDecl):
            if instr.res_name == name:
                return instr.num
        if isinstance(instr, AssignInstr) and name == instr.res:
            return get_const_int(instr.rhs, func)
    print('Error: Cannot find constant', name, 'in\n', func.to_string())
    assert(False)

def evaluate_widths(spec_f):

    new_instrs = []
    for instr in spec_f.instructions:
        if isinstance(instr, CallInstr):
            print(instr)
            f = instr.func
#            if (isinstance(f, ast.Attribute)):
            if (isinstance(f, str)):
                #print('Attribute =', f.attr)
                #assert(f.attr == 'width')
                assert(f == 'width')
                res = instr.res
#                target = f.value
                target = instr.args[0]
                #assert(isinstance(target, ast.Name))
                print('Value =', target)
                width_val = spec_f.symbol_type(target)

                if width_val != None:
                    new_instrs.append(ConstDecl(instr.res, width_val.width()))
                else:
                    # Constraint propagation has not figured out this width yet
                    new_instrs.append(instr)
            else:
                new_instrs.append(instr)
        else:
            new_instrs.append(instr)

    swap_instrs(spec_f, new_instrs)

    new_instrs = []
    for instr in spec_f.instructions:
        print('Second scan')
        if isinstance(instr, CallInstr):
            f = instr.func
            if isinstance(f, ast.Name) and f.id == 'bv_from_int':
                print('Is instance of bv instruction')

                bv_width_name = instr.args[0]
                bv_val_name = instr.args[1]

                print('width =', bv_width_name)
                print('val   =', bv_val_name)

                bv_val = get_const_int(bv_width_name, spec_f)
                bv_width = get_const_int(bv_val_name, spec_f)

                new_instrs.append(ConstBVDecl(instr.res, bv_val, bv_width))
            else:
                new_instrs.append(instr)
        else:
            new_instrs.append(instr)

    swap_instrs(spec_f, new_instrs)

    return

def is_argument_of(v, instr):
    if isinstance(instr, ConstDecl):
        return False
    if isinstance(instr, ConstBVDecl):
        return False
    if isinstance(instr, UnopInstr):
        return instr.in_name == v
    if isinstance(instr, BinopInstr):
        return instr.lhs == v or instr.rhs == v
    if isinstance(instr, ReturnInstr):
        return instr.val_name == v
    if isinstance(instr, SliceInstr):
        return instr.value == v or instr.low == v or instr.high == v
    if isinstance(instr, CompareInstr):
        return instr.lhs == v or instr.rhs == v
    if isinstance(instr, AssignInstr):
        return instr.rhs == v
    if isinstance(instr, ITEInstr):
        return instr.test == v or instr.true_exp == v or instr.false_exp == v
    if isinstance(instr, CallInstr):
        for arg in instr.args:
            if arg == v:
                return True
        return False
    
    print('Error: Unsupported instruction type', instr)
    assert(False)

def is_dead_value(v, func):
    for instr in func.instructions:
        if (is_argument_of(v, instr)):
            return False

    return True

    
def delete_dead_instructions(func):
    new_instrs = []
    for instr in func.instructions:
        if isinstance(instr, BinopInstr) or isinstance(instr, UnopInstr):
            res = instr.res
            if (not is_dead_value(res, func)):
                new_instrs.append(instr)
        elif isinstance(instr, ConstDecl):
            res = instr.res_name
            if (not is_dead_value(res, func)):
                new_instrs.append(instr)
        else:
            new_instrs.append(instr)

    swap_instrs(func, new_instrs)
    #func.instructions = new_instrs

def inline_symtab(receiver, instr):
    for name in instr.used_values():
        if not receiver.has_symbol(name):
            receiver.add_symbol(name, None)

def inline_function(receiver, new_instructions, to_inline, arg_map, returned):
    s = receiver.unique_suffix()
    for instr in to_inline.instructions:
        icpy = copy.deepcopy(instr)
        icpy.replace_values(lambda name: arg_map[name] if name in arg_map else name + '_' + s)
        #replace_values(arg_map, s, icpy)

        inline_symtab(receiver, icpy)
        if not isinstance(icpy, ReturnInstr):
            new_instructions.append(icpy)
        else:
            new_instructions.append(AssignInstr(returned, icpy.val_name))
    return None

def inline_all(f, code_gen):
    new_instructions = []
    for instr in f.instructions:
        if isinstance(instr, CallInstr):
            called_func = instr.func
            if isinstance(called_func, ast.Name) and code_gen.has_function(called_func.id):
                print('User defined function', called_func.id)

                called_func_def = code_gen.get_function(called_func.id)
                arg_map = {}
                i = 0
                for arg in called_func_def.args:
                    arg_map[arg] = instr.args[i]
                    i += 1

                receiver = instr.res
                inline_function(f, new_instructions, called_func_def, arg_map, receiver)
            else:
                new_instructions.append(instr)
        else:
            new_instructions.append(instr)
            
    swap_instrs(f, new_instructions)

def evaluate_integer_constants(f):
    values = {}
    new_instructions = []
    for instr in f.instructions:
        if isinstance(instr, BinopInstr):
            if (instr.lhs in values) and (instr.rhs in values) and isinstance(instr.op, ast.Sub):
                values[instr.res] = values[instr.lhs] - values[instr.rhs]
                new_instructions.append(ConstDecl(instr.res, values[instr.res]))
            else:
                new_instructions.append(instr)

        elif isinstance(instr, ConstDecl):
            values[instr.res_name] = instr.num
            new_instructions.append(instr)
        else:
            new_instructions.append(instr)
    swap_instrs(f, new_instructions)

def specialize_types(code_gen, func_name, func_arg_types):
    spec_name = func_name
    func = code_gen.get_function(func_name)
    sym_map = {}
    i = 0
    for tp in func_arg_types:
        spec_name += '_' + str(tp.width())
        sym_map[func.get_arg(i)] = tp
        i += 1

    spec_f = LowFunctionDef(spec_name, func.args)
    spec_f.unique_num = func.unique_num
    for sym in func.symbol_table:
        spec_f.add_symbol(sym, func.symbol_type(sym))
    for sym in sym_map:
        spec_f.set_symbol_type(sym, sym_map[sym])

    for instr in func.instructions:
        spec_f.instructions.append(instr)

        
    print('Before inlining')
    print(spec_f.to_string())

    inline_all(spec_f, code_gen)

    print('After inlining')
    print(spec_f.to_string())

    evaluate_widths(spec_f)

    print('After evaluating widths first')
    print(spec_f.to_string())

    unify_types(spec_f)
    evaluate_integer_constants(spec_f)

    evaluate_widths(spec_f)
    unify_types(spec_f)
    evaluate_integer_constants(spec_f)

    delete_dead_instructions(spec_f)
    
    print('After second width evaluation')
    print(spec_f.to_string())

    evaluate_widths(spec_f)

    print(spec_f.to_string())

    delete_dead_instructions(spec_f)
    
    return spec_f
