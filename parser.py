import ast

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
        return '\tbinop' + str(self.op) + ' ' + self.res + ' ' + self.lhs + ' ' + self.rhs + '\n'

class UnopInstr(LowInstruction):
    def __init__(self, op, res, in_name):
        self.op = op
        self.res = res
        self.in_name = in_name

    def to_string(self):
        return '\tunop' + str(self.op) + ' ' + self.res + ' ' + self.in_name + '\n'
        
class CallInstr(LowInstruction):
    def __init__(self, res, func, args):
        self.res = res
        self.func = func
        self.args = args

    def to_string(self):
        return '\tcall ' + self.res + ' ' + str(self.func) + '\n'
        
class LowFunctionDef:
    def __init__(self, name, args):
        self.name = name
        self.args = args
        self.instructions = []
        self.unique_num = 0
        self.symbol_table = {}

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
        s = 'function ' + self.name + '('
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
            self.active_function.add_instr(CallInstr(res, expr.func, expr.args))
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
    
class SynthesisConstraints:
    def __init__(self):
        self.num_cycles = 1

class FSM:
    def __init__(self):
        return None

    def num_states(self):
        return 1

def synthesize(code_gen, func_name, arg_widths, constraints):
    return FSM()
