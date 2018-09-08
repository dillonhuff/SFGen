import ast

class LowCodeGenerator(ast.NodeVisitor):
    def __init__(self):
        ast.NodeVisitor.__init__(self)
        self.active_function = None
        self.functions = {}

    def visit_Module(self, node):
        for stmt in node.body:

            if isinstance(stmt, ast.Import):
                self.visit_Import(stmt)
            elif isinstance(stmt, ast.FunctionDef):
                self.visit_FunctionDef(stmt)
            elif isinstance(stmt, ast.Expr):
                print('Log: Synthesis ignores top level expression', ast.dump(stmt))
            else:
                self.generic_visit(stmt)


    def visit_Import(self, node):
        return None
            
    def visit_FunctionDef(self, node):
        assert(self.active_function == None)
        
        print('Function def =', node.name)

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
