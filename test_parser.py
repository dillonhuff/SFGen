from parser import *
import language as l
import ast
from rtl import *

import os

def run_cmd(cmd):
    res = os.system(cmd)
    return res == 0

def run_iverilog_test(mod_name):
    # Compile iverilogmod
    assert(run_cmd('iverilog -o {0} {0}.v {0}_tb.v'.format(mod_name)))
    assert(run_cmd('./{0} > {0}_res.txt'.format(mod_name)))

    f = open('{0}_res.txt'.format(mod_name), 'r')
    res = f.read()
    f.close()

    return res

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

    res = run_iverilog_test(mod.name)

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

    res = run_iverilog_test(mod.name)
    assert(res == 'passed\n')

def test_instr_replacemant():
    call = CallInstr('res', 'func', ['hello', 'no'])
    call.replace_values(lambda name: 'a' if name == 'hello' else name)
    assert(call.args[0] == 'a')
    
def test_newton_raphson_parse():
    code_str = open('divider.py').read()
    code = ast.parse(code_str)

    code_gen = LowCodeGenerator()
    code_gen.visit(code)

    print(code_gen.get_function("newton_raphson_divide").to_string())

    constraints = ScheduleConstraints()
    f_spec = specialize_types(code_gen, "newton_raphson_divide", [l.ArrayType(16), l.ArrayType(16)])

    print('')
    print(f_spec.to_string())

    assert(f_spec.symbol_type('n') == l.ArrayType(16))
    assert(f_spec.symbol_type('d') == l.ArrayType(16))    
    sched = schedule(code_gen, f_spec, constraints)

    print(sched.to_string())

    mod = generate_rtl(f_spec, sched)

    assert(mod.name == f_spec.name)

    generate_verilog(mod)

    res = run_iverilog_test(mod.name)
    assert(res == 'passed\n')
