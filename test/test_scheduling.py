from sfgen.parser import *
import sfgen.language as l
import ast
from sfgen.rtl import *
from sfgen.scheduling import *
from sfgen.utils import *
from sfgen.verilog_backend import generate_verilog

def unit_schedules_same_length(sched):
    subs_pass = True
    for sub in sched.subschedules:
        if not unit_schedules_same_length(sched.subschedules[sub]):
            return False

    sched_len = None
    first_sched = True
    for unit in sched.functional_units:
        s = sched.get_schedule(unit)
        if first_sched:
            sched_len = len(s)
        else:
            if len(s) != sched_len:
                return False

    return True
            
def instructions_in_order(sched, f):
    assert(isinstance(sched, Schedule))
    assert(isinstance(f, LowFunctionDef))

    earlier_instructions = set([])
    print('instructions =', f.instructions)
    print('schedule     =', sched)
    for instr in f.instructions:
        if isinstance(instr, ReturnInstr) or isinstance(instr, ConstDecl):
            continue
        
        binding = sched.get_binding(instr)
        cycle_num = binding[1]

        assert(isinstance(cycle_num, int))

        for earlier in earlier_instructions:
            earlier_cycle = sched.get_binding(earlier)[1]
            if earlier_cycle > cycle_num:
                print('other =', earlier, 'bound at', earlier_cycle)
                print('instr =', instr, 'bound at', cycle_num)
                assert(not earlier in earlier_instructions)
        
        earlier_instructions.add(instr)

    return True

# def test_schedule_with_non_zero_latency():
#     code_gen = codegen_for_module('mult')
#     f_spec = specialize_types(code_gen, 'mult', [l.ArrayType(16), l.ArrayType(16)])
#     constraints = ScheduleConstraints()
#     constraints.set_resource_latency('mult_16', 2)
#     sched = schedule(code_gen, f_spec, constraints)

#     print('non-zero latency sched')
#     print(sched)

#     assert(unit_schedules_same_length(sched))
#     assert(sched.num_cycles() == 7)
#     assert(instructions_in_order(sched, f_spec))

#     mod = generate_rtl(f_spec, sched)

#     assert(mod.name == f_spec.name)

#     generate_verilog(mod)

#     print('Function')
#     print(f_spec.to_string())

#     res = run_iverilog_test(mod.name)
#     assert(res == 'passed\n')
    
def test_schedule():
    code_gen = codegen_for_module('examples/mult')
    f_spec = specialize_types(code_gen, 'mult', [l.ArrayType(8), l.ArrayType(8)])
    constraints = ScheduleConstraints()
    constraints.set_resource_count('mult_8', 1)
    sched = schedule(code_gen, f_spec, constraints)

    assert(sched.num_cycles() == 3)

    assert(instructions_in_order(sched, f_spec))

    mod = generate_rtl(f_spec, sched)

    assert(mod.name == f_spec.name)

    generate_verilog(mod)

    print('Function')
    print(f_spec.to_string())

    res = run_iverilog_test(mod.name)
    assert(res == 'passed\n')
