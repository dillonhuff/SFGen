from parser import *
import language as l
import ast
from rtl import *
from scheduling import *
from utils import *

def test_schedule():
    code_gen = codegen_for_module('mult')
    f_spec = specialize_types(code_gen, 'mult', [l.ArrayType(8), l.ArrayType(8)])
    constraints = ScheduleConstraints()
    constraints.set_resource_count('mult_8', 1)
    sched = schedule(code_gen, f_spec, constraints)

    assert(sched.num_cycles() == 2)

    mod = generate_rtl(f_spec, sched)

    assert(mod.name == f_spec.name)

    generate_verilog(mod)

    res = run_iverilog_test(mod.name)
    assert(res == 'passed\n')
