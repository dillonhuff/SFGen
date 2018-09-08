from parser import *
import ast

def test_tc_neg_parse():
    code_str = open('divider.py').read()
    code = ast.parse(code_str)

    code_gen = LowCodeGenerator()
    code_gen.visit(code)

    print(code_gen.get_function("tc_neg").to_string())

    constraints = SynthesisConstraints()
    fsm = synthesize(code_gen, "tc_neg", [16], constraints)

    assert(False)
    assert(fsm.num_states() == 1)
