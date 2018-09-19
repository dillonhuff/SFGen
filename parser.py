import ast
from language import *
import bit_vector as b
import copy

from utils import *

def substitute_constraint(name, tp, c):
    return (substitute(name, tp, c[0]), substitute(name, tp, c[1]))

def all_ops_same_width(instr):
    if anyinstance(instr.op, [ast.Mult, ast.Add, ast.Sub, ast.Div]):
        return True
    else:
        return False

def is_shift(instr):
    return anyinstance(instr.op, [ast.LShift, ast.RShift])

def anyinstance(i, tps):
    for t in tps:
        if isinstance(i, t):
            return True
    return False

class LowCodeGenerator(ast.NodeVisitor):
    def __init__(self, module_name):
        ast.NodeVisitor.__init__(self)
        self.module_name = module_name
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

            # print('Function call')
            # print(ast.dump(expr))
            
            if is_width_call(expr.func):
                assert(len(expr.args) == 0)

                print('Found width call')
                # print(ast.dump(expr))
                # assert(False)
                self.visit_Expr(expr.func.value)
                assert(expr.func.attr == 'width')
                res = self.active_function.fresh_sym()

                self.active_function.add_instr(CallInstr(res, 'width', [self.expr_name(expr.func.value)]))
            elif is_table_call(expr.func):
                print('Found table call')
                print(ast.dump(expr.func))

                assert(len(expr.args) == 2)
                self.visit_Expr(expr.args[0])

                arg = self.expr_name(expr.args[0])

                table_name = expr.args[1]

                assert(isinstance(table_name, ast.Name))

                res = self.active_function.fresh_sym()
                
                self.active_function.add_instr(TableLookupInstr(res, arg, table_name.id))

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

        fdef = LowFunctionDef(node.name, self.module_name, arg_names)
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
        self.resource_counts = {}

    def set_resource_count(self, resource_name, count):
        self.resource_counts[resource_name] = count

    def is_limited_unit(self, resource_name):
        return resource_name in self.resource_counts

    def available_units(self, resource_name):
        return self.resource_counts[resource_name]
    
class Schedule:
    def __init__(self):
        self.unique_num = 0
        self.functional_units = {}
        self.total_num_cycles = 0

    def num_cycles(self):
        return self.total_num_cycles

    def get_operation(self, name):
        return self.functional_units[name][0]
    
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

    def get_schedule(self, unit_name):
        return self.functional_units[unit_name][1]

    def to_string(self):
        s = '--- Schedule\n'
        for unit in self.functional_units:
            s += '\t' + unit + ' -> ' + str(self.functional_units[unit]) + '\n'
        return s

    def bind_instruction(self, unit_name, start_time, instruction):
        unit = self.functional_units[unit_name]
        sched = self.get_schedule(unit_name)

        assert(len(sched) <= start_time)
        i = len(sched)
        while i < start_time:
            sched.append(None)
            i += 1
        sched.append(instruction)

    def fresh_name(self, prefix):
        n = prefix + '_' + str(self.unique_num)
        self.unique_num += 1
        return n

    def num_units_of_type(self, op_name):
        n = 0
        for u in self.functional_units:
            if self.get_operation(u).name == op_name:
                n += 1

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

    def to_string(self):
        return self.name

    def __repr__(self):
        return self.to_string()

    def __str__(self):
        return self.to_string()

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
    if isinstance(op, ast.LShift):
        return 'shl'
    if isinstance(op, ast.RShift):
        return 'lshr'
    if isinstance(op, ast.Sub):
        return 'sub'
    if isinstance(op, ast.Div):
        return 'unsigned_div'
    if isinstance(op, ast.Mult):
        return 'mult'
    if isinstance(op, ast.NotEq):
        return 'not_eq'

    print('Unsupported op =', op)

    assert(False)

sameWidthOps = [ast.Invert, ast.Add, ast.Sub]

def functional_unit(instr, f):
    if isinstance(instr, BinopInstr) and is_shift(instr):
        name = op_string(instr.op)
        l_width = f.symbol_type(instr.lhs).width()
        r_width = f.symbol_type(instr.rhs).width()
        name += '_' + str(l_width) + '_' + str(r_width)
        return Operation(name, [l_width, r_width])
        
    if isinstance(instr, BinopInstr) or isinstance(instr, UnopInstr):
        name = op_string(instr.op)
        width = f.symbol_type(instr.res).width()
        name += '_' + str(width)

        return Operation(name, [width])
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
    elif isinstance(instr, CallInstr) and isinstance(instr.func, ast.Name) and (instr.func.id == 'leading_zero_count'):

        print('lead zero args')
        for arg in instr.args:
            print(arg)
        assert(len(instr.args) == 1)

        width = f.symbol_type(instr.args[0]).width()
        return Operation(instr.func.id + '_' + str(width), [width])

    elif isinstance(instr, CallInstr) and isinstance(instr.func, ast.Name) and (instr.func.id == 'zero_extend'):

        assert(len(instr.args) == 2)

        out_width = f.get_int_constant_value(instr.args[0])
        in_width = f.symbol_type(instr.args[1]).width()
        return Operation(instr.func.id + '_' + str(out_width) + '_' + str(in_width), [out_width, in_width])
    elif isinstance(instr, CallInstr) and isinstance(instr.func, ast.Name) and (instr.func.id == 'concat'):
        assert(len(instr.args) == 2)

        in0_width = f.symbol_type(instr.args[0]).width()
        in1_width = f.symbol_type(instr.args[1]).width()
        return Operation(instr.func.id + '_' + str(in0_width) + '_' + str(in1_width), [in0_width, in1_width])
        
    elif isinstance(instr, CallInstr):
        assert(isinstance(instr.func, ast.Name))
        assert(False)

    elif isinstance(instr, TableLookupInstr):
        return Operation('builtin_table_lookup_' + instr.table_name, [f.symbol_type(instr.arg).width(), f.symbol_type(instr.res).width(), instr.table_name, f.get_module_name()])

    elif isinstance(instr, ITEInstr):
        width = f.symbol_type(instr.res).width()
        return Operation('ite_' + str(width), [width])
    elif isinstance(instr, SliceInstr):
        high_val = f.get_int_constant_value(instr.high)
        low_val = f.get_int_constant_value(instr.low)
        in_width = f.symbol_type(instr.value).width()
        return Operation('slice_' + str(in_width) + '_' + str(low_val) + '_' + str(high_val), [in_width, low_val, high_val])

    print('Unsupported functional unit', instr)
    assert(False)

def get_unit(op, constraints, s, cycle_time):
    num_units = s.num_units_of_type(op.name)
    print('# of units of type', op, '=', num_units)
    if not constraints.is_limited_unit(op.name) or s.num_units_of_type(op.name) < constraints.available_units(op.name):
        return s.add_unit(op)

    for unit in s.functional_units:
        n = s.get_operation(unit).name
        print('n = ', n)
        if n == op.name:
            unit_sched = s.get_schedule(unit)
            print('Unit sched =', unit_sched)
            if len(unit_sched) <= cycle_time:
                return unit

    print('Cannot schedule', op, 'at time', cycle_time)
    return None
    
def schedule(code_gen, f, constraints):
    s = Schedule()
    cycle_num = 0
    bound_instructions = set([])
    unbound_instructions = set(f.instructions)

    cycle_time = 0

    while len(bound_instructions) < len(f.instructions):

        instr = next(iter(unbound_instructions))

        bound = True
        if not isinstance(instr, ReturnInstr) and not isinstance(instr, ConstDecl):
            opN = functional_unit(instr, f)
            op = opN.name

            unit_name = get_unit(functional_unit(instr, f), constraints, s, cycle_time)

            if unit_name == None:
                #print('Combinational schedule needs at least', units_used, 'of operation:', op, 'but only', constraints.available_units(op), 'are available. Adding a cycle')

                cycle_time += 1
                bound = False
            else:
                s.bind_instruction(unit_name, cycle_time, instr)
        else:
            bound_instructions.add(instr)

        if bound:
            bound_instructions.add(instr)
            unbound_instructions.remove(instr)

    s.total_num_cycles = cycle_time

    # Check that resource usage matches synthesis constraints
    total_resources = {}
    print('Units')
    for unit in s.functional_units:
        op_name = s.get_operation(unit).name
        if op_name in total_resources:
            total_resources[op_name] += 1
        else:
            total_resources[op_name] = 1

    print('Resources used')
    for r in total_resources:
        print('\t', r, ' -> ', total_resources[r])

    for r in constraints.resource_counts:
        max_val = constraints.resource_counts[r]
        if r in total_resources and max_val < total_resources[r]:
            print('Error: Too many uses of', r)
            print('r          =', r)
            print('max use    =', max_val)
            print('actual use =', total_resources[r])
            assert(False)

    return s

def get_primitives(c):
    if isinstance(c[0], Type) and isinstance(c[1], str):
        return (c[1], c[0])
    if isinstance(c[1], Type) and isinstance(c[0], str):
        return (c[0], c[1])

    return None

def substitute(name, tp, c):
    if c == name:
        return tp
    else:
        return c

def get_const_int(name, func):
    for instr in func.instructions:
        if isinstance(instr, ConstDecl):
            if instr.res_name == name:
                return instr.num
        if isinstance(instr, AssignInstr) and name == instr.res:
            return get_const_int(instr.rhs, func)

    return None

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
    if isinstance(instr, TableLookupInstr):
        return v in instr.arguments()
    
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
        if isinstance(instr, BinopInstr) or isinstance(instr, UnopInstr) or isinstance(instr, AssignInstr):
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

def inline_funcs(f, code_gen):
    inlined_any = False
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
                inlined_any = True
            else:
                new_instructions.append(instr)
        else:
            new_instructions.append(instr)
            
    swap_instrs(f, new_instructions)
    return inlined_any

def inline_all(f, code_gen):
    inlined = inline_funcs(f, code_gen)
    while inlined:
        inlined = inline_funcs(f, code_gen)

def evaluate_int_unop(new_instructions, f, instr, values):
    if isinstance(instr.op, ast.Invert):
        values[instr.res] = ~values[instr.in_name]
        new_instructions.append(ConstDecl(instr.res, values[instr.res]))

    assert(False)
    
def evaluate_int_binop(new_instructions, f, instr, values):
    if isinstance(instr.op, ast.Sub):
        values[instr.res] = values[instr.lhs] - values[instr.rhs]
        new_instructions.append(ConstDecl(instr.res, values[instr.res]))
    elif isinstance(instr.op, ast.Mult):
        values[instr.res] = values[instr.lhs] * values[instr.rhs]
        new_instructions.append(ConstDecl(instr.res, values[instr.res]))
    elif isinstance(instr.op, ast.Add):
        values[instr.res] = values[instr.lhs] + values[instr.rhs]
        new_instructions.append(ConstDecl(instr.res, values[instr.res]))

    elif isinstance(instr.op, ast.FloorDiv):
        values[instr.res] = values[instr.lhs] // values[instr.rhs]
        new_instructions.append(ConstDecl(instr.res, values[instr.res]))

    elif isinstance(instr.op, ast.Div):
        values[instr.res] = values[instr.lhs] / values[instr.rhs]
        new_instructions.append(ConstDecl(instr.res, values[instr.res]))

    elif isinstance(instr.op, ast.FloorDiv):
        values[instr.res] = values[instr.lhs] // values[instr.rhs]
        new_instructions.append(ConstDecl(instr.res, values[instr.res]))
    else:
        print('Unsupported binop', instr)
        assert(False)

    f.set_symbol_type(instr.res, IntegerType())

def evaluate_integer_constants(f, code_gen):
    values = {}
    new_instructions = []
    for instr in f.instructions:
        if isinstance(instr, BinopInstr):
            lhs_tp = f.symbol_type(instr.lhs)
            rhs_tp = f.symbol_type(instr.rhs)

            print('binop =', instr)
            print('Lhs   =', instr.lhs, ':', lhs_tp)
            print('Rhs   =', instr.rhs, ':', rhs_tp)

            assert(lhs_tp != None)
            assert(rhs_tp != None)
            #assert(rhs_tp == lhs_tp)

            if (instr.lhs in values) and (instr.rhs in values):
                evaluate_int_binop(new_instructions, f, instr, values)
            else:
                new_instructions.append(instr)
                f.set_symbol_type(instr.res, lhs_tp)

        elif isinstance(instr, UnopInstr):
            lhs_tp = f.symbol_type(instr.in_name)

            print('OpT =', instr.in_name, ':', lhs_tp)

            assert(lhs_tp != None)

            if (instr.in_name in values):
                evaluate_int_unop(new_instructions, f, instr, values)
            else:
                new_instructions.append(instr)
                f.set_symbol_type(instr.res, lhs_tp)

        elif isinstance(instr, ITEInstr):
            new_instructions.append(instr)

            test_tp = f.symbol_type(instr.test)
            assert(test_tp == ArrayType(1))
            
            true_tp = f.symbol_type(instr.true_exp)
            false_tp = f.symbol_type(instr.false_exp)

            assert(true_tp == false_tp)
            assert(isinstance(true_tp, ArrayType))

            f.set_symbol_type(instr.res, true_tp)
            
        elif isinstance(instr, CompareInstr):
            f.set_symbol_type(instr.res, ArrayType(1))
            new_instructions.append(instr)

        elif isinstance(instr, AssignInstr):
            assert(f.symbol_type(instr.rhs) != None)
            
            f.set_symbol_type(instr.res, f.symbol_type(instr.rhs))
            if instr.rhs in values:
                values[instr.res] = values[instr.rhs]
            new_instructions.append(instr)

            
        elif isinstance(instr, CallInstr) and instr.func == 'width':
            assert(len(instr.args) == 1)
            if isinstance(f.symbol_type(instr.args[0]), ArrayType):
                values[instr.res] = f.symbol_type(instr.args[0]).width()
                new_instructions.append(ConstDecl(instr.res, values[instr.res]))
                f.set_symbol_type(instr.res, IntegerType())
            else:
                print('After specializing func')
                print(f.to_string())
                print('Error: Bad type on argument of', instr)
                assert(False)
                #new_instructions.append(instr)

        elif isinstance(instr, CallInstr) and isinstance(instr.func, ast.Name) and instr.func.id == 'leading_zero_count':
            assert(len(instr.args) == 1)
            if isinstance(f.symbol_type(instr.args[0]), ArrayType):
                new_instructions.append(instr)
                f.set_symbol_type(instr.res, f.symbol_type(instr.args[0]))
            else:
                assert(False)
                #new_instructions.append(instr)
                
        elif isinstance(instr, CallInstr) and isinstance(instr.func, ast.Name) and instr.func.id == 'concat':
            assert(len(instr.args) == 2)
            if isinstance(f.symbol_type(instr.args[0]), ArrayType) and isinstance(f.symbol_type(instr.args[1]), ArrayType):
                f.set_symbol_type(instr.res, ArrayType(f.symbol_type(instr.args[0]).width() + f.symbol_type(instr.args[1]).width()))
            new_instructions.append(instr)

        elif isinstance(instr, CallInstr) and isinstance(instr.func, ast.Name) and instr.func.id == 'bv_from_int':

            bv_width_name = instr.args[0]
            bv_val_name = instr.args[1]

            # bv_val = get_const_int(bv_width_name, f)
            # bv_width = get_const_int(bv_val_name, f)

            bv_val = values[bv_val_name]
            bv_width = values[bv_width_name]
            print('bv_val   =', bv_val)
            print('bv_width =', bv_width)

            if bv_val != None and bv_width != None:
                new_instructions.append(ConstBVDecl(instr.res, bv_width, bv_val))
                f.set_symbol_type(instr.res, ArrayType(bv_width))
            else:
                print('Error: Unset types for call', instr, 'val =', bv_val)
                assert(False)
                #new_instructions.append(instr)

        elif isinstance(instr, CallInstr) and isinstance(instr.func, ast.Name) and instr.func.id == 'zero_extend':

            w = instr.args[0]
            tp = f.symbol_type(w)

            assert(w in values)
            assert(isinstance(tp, IntegerType))

            f.set_symbol_type(instr.res, ArrayType(values[w]))

            new_instructions.append(instr)

        elif isinstance(instr, CallInstr) and isinstance(instr.func, ast.Name) and instr.func.id == 'lookup_in_table':

            print('Found table lookup')

            arg = instr.args[0]
            table_func_name = instr.args[1]

            print('arg   =', arg)
            print('table =', table_func_name)

            # assert(w in values)
            # assert(isinstance(tp, l.IntegerType))

            # f.set_symbol_type(instr.res, l.ArrayType(values[w]))

            new_instructions.append(instr)

            assert(False)
            
        elif isinstance(instr, CallInstr):
            print('Error: Unhandled call', instr)
            assert(False)
            #new_instructions.append(instr)

        elif isinstance(instr, ReturnInstr):
            new_instructions.append(instr)

        elif isinstance(instr, ConstBVDecl):
            new_instructions.append(instr)
            
        elif isinstance(instr, ConstDecl):
            values[instr.res_name] = instr.num
            new_instructions.append(instr)
            f.set_symbol_type(instr.res_name, IntegerType())

        elif isinstance(instr, SliceInstr):
            if instr.low in values and instr.high in values:
                high_val = values[instr.high]
                low_val = values[instr.low]
                f.set_symbol_type(instr.res, ArrayType(high_val - low_val + 1))
            else:
                print('Error: Bad types on arguments to', instr)
                assert(False)
            new_instructions.append(instr)

        elif isinstance(instr, TableLookupInstr):
            t = f.symbol_type(instr.arg)
            assert(isinstance(t, ArrayType))

            print('Name = ', instr.table_name)
            
            called_func = code_gen.get_function(instr.table_name)
            assert(len(called_func.args) == 1)

            print('Specializing', instr.table_name, 'for type', t)
            spec_func = specialize_types(code_gen, instr.table_name, [t])
            print('Done specializing')

            assert(isinstance(spec_func.instructions[-1], ReturnInstr))

            res_tp = spec_func.symbol_type(spec_func.instructions[-1].val_name)
            assert(res_tp != None)

            print('res_tp =', res_tp)
            f.set_symbol_type(instr.res, res_tp)
            f.set_symbol_type(instr.table_name, FunctionType([t], res_tp))

            new_instructions.append(instr)

        else:
            print('Error: Evaluating constants for unhandled instruction', instr)
            assert(False)
            new_instructions.append(instr)
    swap_instrs(f, new_instructions)

def simplify_integer_assigns(spec_f):

    new_instructions = []
    replaced = set()
    for i in range(0, len(spec_f.instructions)):
        instr = spec_f.instructions[i]
        if isinstance(instr, AssignInstr) and (spec_f.symbol_type(instr.res) == IntegerType()):
            replaced.add(instr.res)

            for j in range(i + 1, len(spec_f.instructions)):
                
                spec_f.instructions[j].replace_values(lambda name: instr.rhs if name == instr.res else name)

        else:
            new_instructions.append(instr)

    swap_instrs(spec_f, new_instructions)

    # Check that replacement really happened
    not_replaced = False
    for val in replaced:
        for instr in spec_f.instructions:
            if val in instr.used_values():
                print('Error: Value', val, 'was supposed to be replaced, but it still exists in', instr)
                not_replaced = True
    assert(not not_replaced)

def func_name(instr):
    assert(isinstance(instr, CallInstr))
    if isinstance(instr.func, str):
        return instr.func

    assert(isinstance(instr.func, ast.Name))
    return instr.func.id

def is_builtin(func_name):
    if func_name == 'zero_extend':
        return True

    if func_name == 'concat':
        return True
    
    if func_name == 'bv_from_int':
        return True

    if func_name == 'leading_zero_count':
        return True

    if func_name == 'width':
        return True

    if func_name == 'lookup_in_table':
        return True
    
    return False

def is_synthesizable(func, spec_f, code_gen):
    return code_gen.has_function(func) or is_builtin(func)

def delete_unsynthesizable_instructions(spec_f, code_gen):
    new_instrs = []
    for instr in spec_f.instructions:
        if isinstance(instr, CallInstr):
            if is_synthesizable(func_name(instr), spec_f, code_gen):
                new_instrs.append(instr)
            else:
                print('Removing un-synthesizable function', func_name(instr))
        else:
            new_instrs.append(instr)
            
    swap_instrs(spec_f, new_instrs)
    
def specialize_types(code_gen, func_name, func_arg_types):
    assert(isinstance(func_name, str))

    spec_name = func_name
    func = code_gen.get_function(func_name)
    sym_map = {}
    i = 0
    for tp in func_arg_types:
        spec_name += '_' + str(tp.width())
        sym_map[func.get_arg(i)] = tp
        i += 1

    spec_f = LowFunctionDef(spec_name, func.get_module_name(), func.args)
    spec_f.unique_num = func.unique_num
    for sym in func.symbol_table:
        spec_f.add_symbol(sym, func.symbol_type(sym))
    for sym in sym_map:
        spec_f.set_symbol_type(sym, sym_map[sym])

    for instr in func.instructions:
        spec_f.instructions.append(copy.deepcopy(instr))
        
    # print('Before inlining')
    # print(spec_f.to_string())

    inline_all(spec_f, code_gen)
    delete_unsynthesizable_instructions(spec_f, code_gen)
    delete_dead_instructions(spec_f)
    
    # print('After inlining')
    # print(spec_f.to_string())

    evaluate_integer_constants(spec_f, code_gen)

    # print('After evaluating widths first')
    # print(spec_f.to_string())

    simplify_integer_assigns(spec_f)
    delete_dead_instructions(spec_f)

    # print('After second width evaluation')
    # print(spec_f.to_string())

    all_values = set()
    for instr in spec_f.instructions:
        for value in instr.used_values():
            all_values.add(value)
            if spec_f.symbol_type(value) == None:
                print('Error: Symbol', value, 'is used in', instr, 'but has no type')
                assert(False)

    to_erase = set()
    for s in spec_f.symbol_table:
        if not s in all_values:
            to_erase.add(s)

    for s in to_erase:
        spec_f.erase_symbol(s)

    # print('Final specialized functions')
    # print(spec_f.to_string())

    return spec_f

def codegen_for_module(mod_name):
    code_str = open(mod_name + '.py').read()
    code = ast.parse(code_str)
    code_gen = LowCodeGenerator(mod_name)
    code_gen.visit(code)

    return code_gen
