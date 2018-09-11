from parser import *
import language as l
import ast
from rtl import *

import os
def run_cmd(cmd):
    res = os.system(cmd)
    return res == 0

def test_tc_neg_parse():
    code_str = open('tc_neg.py').read()
    code = ast.parse(code_str)

    code_gen = LowCodeGenerator()
    code_gen.visit(code)

    print(code_gen.get_function("tc_neg").to_string())

    constraints = ScheduleConstraints()
    f_spec = specialize_types(code_gen, "tc_neg", [l.ArrayType(16)])

    print('')
    print(f_spec.to_string())

    assert(f_spec.symbol_type('a') == l.ArrayType(16))
    
    sched = schedule(code_gen, f_spec, constraints)

    assert(sched.num_states() == 1)

    # One add, one invert, one constant
    assert(sched.num_functional_units() == 3)

    assert(sched.get_binding(f_spec.instructions[0]) == ("invert_16_0", 0))

    print(sched.to_string())
    mod = generate_rtl(f_spec, sched)

    assert(mod.name == f_spec.name)

    generate_verilog(mod)

    # Compile iverilog
    assert(run_cmd('iverilog -o {0} {0}.v {0}_tb.v'.format(mod.name)))
    assert(run_cmd('./{0} > {0}_res.txt'.format(mod.name)))

    f = open('{0}_res.txt'.format(mod.name), 'r')
    res = f.read()
    f.close()

    assert(res == 'passed\n')
    
def test_tc_abs_parse():
    code_str = open('tc_abs.py').read()
    code = ast.parse(code_str)

    code_gen = LowCodeGenerator()
    code_gen.visit(code)

    print(code_gen.get_function("tc_abs").to_string())

    constraints = ScheduleConstraints()
    f_spec = specialize_types(code_gen, "tc_abs", [l.ArrayType(16)])

    print('')
    print(f_spec.to_string())

    assert(f_spec.symbol_type('a') == l.ArrayType(16))
    
    sched = schedule(code_gen, f_spec, constraints)

    print(sched.to_string())

    mod = generate_rtl(f_spec, sched)

    assert(mod.name == f_spec.name)

    generate_verilog(mod)

    # Compile iverilog
    assert(run_cmd('iverilog -o {0} {0}.v {0}_tb.v'.format(mod.name)))
    assert(run_cmd('./{0} > {0}_res.txt'.format(mod.name)))

    f = open('{0}_res.txt'.format(mod.name), 'r')
    res = f.read()
    f.close()

    assert(res == 'passed\n')
    
