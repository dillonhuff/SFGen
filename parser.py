import ast
from language import *
import bit_vector as b
import copy

from utils import *

def name_string(n):
    if isinstance(n, ast.Name):
        return n.id
    assert(isinstance(n, str))
    return n

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
        self.active_class = None
        self.functions = {}
        self.classes = {}
        self.expr_names = {}

    def get_function(self, name):
        if isinstance(name, str):
            assert(name in self.functions)
            return self.functions[name]
        else:
            assert(name.id in self.functions)
            return self.functions[name.id]

    def has_function(self, name):
        return name in self.functions

    def has_class(self, name):
        return name in self.classes
    
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

        elif isinstance(stmt, ast.ClassDef):
            self.visit_ClassDef(stmt)
        else:
            self.generic_visit(stmt)
        
    def visit_Module(self, node):
        for stmt in node.body:
            self.visit_Stmt(stmt)


    def expr_name(self, expr):
        if not expr in self.expr_names:
            print('Error:', ast.dump(expr), 'is not in ', self.expr_names)
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

            # elif self.is_class_constructor_call(expr):
            #     arg_exprs = []
            #     for arg in expr.args:
            #         self.visit_Expr(arg)
            #         arg_exprs.append(self.expr_name(arg))
            #     self.active_function.add_instr(CallInstr(res, expr.func, arg_exprs))

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

        elif isinstance(expr, ast.Attribute):
            self.visit_Expr(expr.value)
            assert(isinstance(expr.attr, str))
            res = self.active_function.fresh_sym()
            self.active_function.add_instr(ReadFieldInstr(res, self.expr_name(expr.value), expr.attr))
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

        print('Return =', ast.dump(node))
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

    def visit_ClassDef(self, node):
        assert(self.active_class == None)

        print('Class def =', ast.dump(node))

        class_def = LowClassDef(node.name, {})
        self.classes[node.name] = class_def

        self.active_class = None

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

    if isinstance(instr, ReadFieldInstr):
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

def inline_function(receiver, new_instructions, to_inline, arg_map, returned):
    s = receiver.unique_suffix()
    name_map = {}
    for instr in to_inline.instructions:
        icpy = copy.deepcopy(instr)

        for n in icpy.used_values():
            inlined_name = arg_map[n] if n in arg_map else n + '_' + s
            receiver.add_symbol(inlined_name, to_inline.symbol_type(n))
            
        icpy.replace_values(lambda name: arg_map[name] if name in arg_map else name + '_' + s)

        if not isinstance(icpy, ReturnInstr):
            new_instructions.append(icpy)
        else:
            new_instructions.append(AssignInstr(returned, icpy.val_name))
    return None

def inline_funcs(f, code_gen, functions_to_skip):
    inlined_any = False
    new_instructions = []
    for instr in f.instructions:
        if isinstance(instr, CallInstr):
            called_func = instr.func
            if code_gen.has_function(name_string(called_func)) and not (name_string(called_func) in functions_to_skip):
                print('User defined function', name_string(called_func))

                called_func_def = code_gen.get_function(name_string(called_func))
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

def inline_all(f, code_gen, dont_inline):
    inlined = inline_funcs(f, code_gen, dont_inline)
    while inlined:
        inlined = inline_funcs(f, code_gen, dont_inline)

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

def evaluate_integer_constants(values, f, code_gen):
#    values = {}
    new_instructions = []
    for instr in f.instructions:
        if isinstance(instr, BinopInstr):
            lhs_tp = f.symbol_type(instr.lhs)
            rhs_tp = f.symbol_type(instr.rhs)

            # print('binop =', instr)
            # print('Lhs   =', instr.lhs, ':', lhs_tp)
            # print('Rhs   =', instr.rhs, ':', rhs_tp)

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

            print('Name = ', instr)

            called_func = code_gen.get_function(instr.func)

            #assert(len(called_func.args) == 1)

            #print('Specializing in', f.to_string())
            tps = []
            for arg in instr.args:
                arg_tp = f.symbol_type(arg)
                assert(isinstance(arg_tp, ArrayType) or isinstance(arg_tp, IntegerType))
                if isinstance(arg_tp, ArrayType):
                    tps.append(arg_tp)
                else:
                    tps.append(values[arg])

            print('Specializing', instr.func, 'for types', tps)

            spec_func = specialize_types(code_gen, instr.func, tps)
            print('Done specializing')

            assert(isinstance(spec_func.instructions[-1], ReturnInstr))

            res_tp = spec_func.symbol_type(spec_func.instructions[-1].val_name)
            assert(res_tp != None)

            print('res_tp =', res_tp)
            f.set_symbol_type(instr.res, res_tp)
            f.set_symbol_type(name_string(instr.func), FunctionType(tps, res_tp))

            code_gen.functions[name_string(spec_func.get_name())] = spec_func

            new_instructions.append(CallInstr(instr.res, spec_func.get_name(), instr.args))
            
            #print('Error: Unhandled call', new_instructions[-1])

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
    return code_gen.has_function(func) or code_gen.has_class(func) or is_builtin(func)

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

def make_result_names_unique(f):
    used_names = {}
    for i in range(len(f.instructions)):
        instr = f.instructions[i]

        if not isinstance(instr, ReturnInstr):
            old_name = instr.result_name()

            if old_name in used_names:
                used_names[instr.result_name()] += 1
                next_num = used_names[instr.result_name()]


                new_name = instr.result_name() + '_' + str(next_num)
                
                for j in range(i, len(f.instructions)):
                    other = f.instructions[j]
                    other.replace_values(lambda name : new_name if name == old_name else name)
            else:
                used_names[old_name] = 0

def specialize_types(code_gen, func_name_in, func_arg_types):


    func_name = func_name_in
    if not isinstance(func_name_in, str):
        assert(isinstance(func_name_in, ast.Name))
        func_name = func_name_in.id

    spec_name = func_name
    func = code_gen.get_function(func_name)
    sym_map = {}
    values = {}
    i = 0
    for tp in func_arg_types:
        if isinstance(tp, Type):
            if isinstance(tp, ArrayType):
                spec_name += '_' + str(tp.width())
            sym_map[func.get_arg(i)] = tp
        else:
            assert(isinstance(tp, int))
            spec_name += '_' + str(tp)
            sym_map[func.get_arg(i)] = IntegerType()
            values[func.get_arg(i)] = tp
        i += 1

    spec_f = LowFunctionDef(spec_name, func.get_module_name(), func.args)
    spec_f.unique_num = func.unique_num
    for sym in func.symbol_table:
        spec_f.add_symbol(sym, func.symbol_type(sym))
    for sym in sym_map:
        spec_f.set_symbol_type(sym, sym_map[sym])

    for instr in func.instructions:
        spec_f.instructions.append(copy.deepcopy(instr))
        

    #inline_all(spec_f, code_gen)
    delete_unsynthesizable_instructions(spec_f, code_gen)
    delete_dead_instructions(spec_f)
    
    make_result_names_unique(spec_f)

    evaluate_integer_constants(values, spec_f, code_gen)

    simplify_integer_assigns(spec_f)
    delete_dead_instructions(spec_f)

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

    print('After specializing', name_string(spec_f.get_name()), 'context has functions')
    for f_name in code_gen.functions:
        print('\t', f_name)

    return spec_f

def codegen_for_module(mod_name):
    code_str = open(mod_name + '.py').read()
    code = ast.parse(code_str)
    code_gen = LowCodeGenerator(mod_name)
    code_gen.visit(code)

    return code_gen

# Idea: Preventing power viruses? Use solvers to fix this problem?
