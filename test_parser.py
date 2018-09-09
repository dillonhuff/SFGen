from parser import *
import language as l
import ast

def test_tc_neg_parse():
    code_str = open('divider.py').read()
    code = ast.parse(code_str)

    code_gen = LowCodeGenerator()
    code_gen.visit(code)

    print(code_gen.get_function("tc_neg").to_string())

    constraints = ScheduleConstraints()
    f_spec = specialize_types(code_gen, "tc_neg", [l.ArrayType(16)])

    print(f_spec.to_string())
    
    sched = schedule(code_gen, "tc_neg", [16], constraints)

    assert(sched.num_states() == 1)

    assert(sched.num_functional_units() == 2)
