from parser import *
import language as l
from rtl import *
from scheduling import *
from utils import *
from verilog_backend import *
    
code_gen = codegen_for_module('cube')
f_spec = specialize_types(code_gen, 'cube', [l.ArrayType(32)])

constraints = ScheduleConstraints()
constraints.set_resource_count('mult_32', 1)
sched = schedule(code_gen, f_spec, constraints)

print(sched.to_string())

mod = generate_rtl(f_spec, sched)

assert(mod.name == f_spec.name)

generate_verilog(mod)


