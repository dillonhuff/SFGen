import ast
import language as l
import bit_vector as b

def comma_list(strs):
    ls = ''
    for i in range(0, len(strs)):
        s = strs[i]
        ls += s
        if (i < len(strs) - 1):
            ls += ', '
        
    return ls

class LowInstruction:
    def __init__(self):
        return None

    def to_string(self):
        return '\tUNKNOWN_INSTR\n'

class ConstDecl:
    def __init__(self, res_name, num):
        self.res_name = res_name
        self.num = num

    def to_string(self):
        return '\tconst ' + self.res_name + ' ' + str(self.num) + '\n'

class ConstBVDecl:
    def __init__(self, res_name, width, val):
        self.res_name = res_name
        self.value = b.bv_from_int(width, val)

    def to_string(self):
        return '\tconstbv ' + self.res_name + ' ' + str(self.value) + '\n'
    
class ReturnInstr(LowInstruction):
    def __init__(self, name):
        self.val_name = name

    def to_string(self):
        return '\treturn ' + self.val_name + '\n'

class BinopInstr(LowInstruction):
    def __init__(self, op, res, lhs, rhs):
        self.op = op
        self.res = res
        self.lhs = lhs
        self.rhs = rhs

    def to_string(self):
        return '\tbinop ' + str(self.op) + ' ' + self.res + ' ' + self.lhs + ' ' + self.rhs + '\n'

class UnopInstr(LowInstruction):
    def __init__(self, op, res, in_name):
        self.op = op
        self.res = res
        self.in_name = in_name

    def to_string(self):
        return '\tunop ' + str(self.op) + ' ' + self.res + ' ' + self.in_name + '\n'
        
class CallInstr(LowInstruction):
    def __init__(self, res, func, args):
        self.res = res
        self.func = func
        self.args = args

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
        for arg in args:
            self.symbol_table[arg] = None

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
        self.instructions.append(instr)
        
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

    def visit_Stmt(self, stmt):

        if isinstance(stmt, ast.Import):
            self.visit_Import(stmt)
        elif isinstance(stmt, ast.ImportFrom):
            self.visit_ImportFrom(stmt)
        elif isinstance(stmt, ast.FunctionDef):
            self.visit_FunctionDef(stmt)
        elif isinstance(stmt, ast.Expr):
            if self.active_function == None:
                print('Log: Synthesis ignores top level expression', ast.dump(stmt))
            else:
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
            arg_exprs = []
            for arg in expr.args:
                self.visit_Expr(arg)
                arg_exprs.append(self.expr_name(arg))
            self.active_function.add_instr(CallInstr(res, expr.func, arg_exprs))
            self.expr_names[expr] = res

        elif isinstance(expr, ast.Num):
            n = self.active_function.fresh_sym()
            self.active_function.add_instr(ConstDecl(n, expr.n))
            self.expr_names[expr] = n
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
    
class ScheduleConstraints:
    def __init__(self):
        self.num_cycles = 1

class Schedule:
    def __init__(self):
        self.functional_units = []

    def add_unit(self, unit):
        self.functional_units.append((unit, []))

    def num_states(self):
        return 1

    def num_functional_units(self):
        return len(self.functional_units)

class FunctionalUnit:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

def functional_unit(instr):
    return FunctionalUnit("add")

def schedule(code_gen, func_name, arg_widths, constraints):
    f = code_gen.get_function(func_name)
    s = Schedule()
    for instr in f.instructions:
        s.add_unit(functional_unit(instr))

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

def unify_types(spec_f, f):
    constraints = []
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
        elif isinstance(instr, ConstDecl):
            res = instr.res_name
            constraints.append((res, l.IntegerType))
        else:
            print('Error: Cannot unify types in instruction', instr.to_string)

    print('Type constraints')
    for c in constraints:
        print(c)

    assert(False)

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

        
        new_constraints = []
        for i in range(0, len(constraints)):
            if i != ind:
                other = constraints[i]
                rs = substitute_constraint(primitives[0], primitives[1], other)
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
    print('Error: Cannot find constant', name, 'in\n', func.to_string())
    assert(False)
# TODO: Unpack width calls so that the inner expression is available
def evaluate_widths(spec_f):

    width_values = {}
    new_instrs = []
    for instr in spec_f.instructions:
        if isinstance(instr, CallInstr):
            print(instr)
            f = instr.func
            if (isinstance(f, ast.Attribute)):

                print('Attribute =', f.attr)
                assert(f.attr == 'width')
                res = instr.res
                target = f.value
                assert(isinstance(target, ast.Name))
                print('Value =', ast.dump(target))
                width_values[res] = spec_f.symbol_type(target.id).width()

                new_instrs.append(ConstDecl(instr.res, width_values[res]))
            else:
                new_instrs.append(instr)
            # elif isinstance(f, ast.Name):
            #     assert(f.id == 'bv_from_int')
            #     bv_width_name = instr.args[0]
            #     bv_val_name = instr.args[1]

            #     print('width =', bv_width_name)
            #     print('val   =', bv_val_name)

            #     bv_val = get_const_int(bv_width_name, spec_f)
            #     bv_width = get_const_value(bv_val_name,)

            #     new_instrs.append(ConstBVDecl(instr.res, bv_val, bv_width))
            #     assert(False) # Lookup values and create constant!
#            else:
        else:
            new_instrs.append(instr)

    print('Width values')
    for w in width_values:
        print(w, ' -> ', width_values[w])

    spec_f.instructions = new_instrs

    new_instrs = []
    for instr in spec_f.instructions:
        print('Second scan')
        if isinstance(instr, CallInstr):
            print(instr)
            f = instr.func
            if isinstance(f, ast.Name):
                print('Is instance')
                assert(f.id == 'bv_from_int')
                bv_width_name = instr.args[0]
                bv_val_name = instr.args[1]

                print('width =', bv_width_name)
                print('val   =', bv_val_name)

                bv_val = get_const_int(bv_width_name, spec_f)
                bv_width = get_const_int(bv_val_name, spec_f)

                new_instrs.append(ConstBVDecl(instr.res, bv_val, bv_width))
            else:
                assert(False)
        else:
            new_instrs.append(instr)

    spec_f.instructions = new_instrs
    
    #print('New instrs = ', spec_f.to_string())

    return

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

    unify_types(spec_f, func)

    for instr in func.instructions:
        spec_f.instructions.append(instr)

    print(spec_f.to_string())

    evaluate_widths(spec_f)

    print(spec_f.to_string())
    
    assert(False)

    return spec_f
