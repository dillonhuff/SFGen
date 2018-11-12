import sys
import os.path

print('path =', sys.path)
sys.path.append(os.path.abspath(os.path.join('.', os.pardir)))
print('path =', sys.path)

from sfgen.parser import *
import sfgen.language as l
from sfgen.rtl import *
from sfgen.scheduling import *
from sfgen.utils import *
from sfgen.verilog_backend import *
    
code_gen = codegen_for_module('examples/cube')
f_spec = specialize_types(code_gen, 'cube', [l.ArrayType(32)])

constraints = ScheduleConstraints()
constraints.set_resource_count('mult_32', 1)
sched = schedule(code_gen, f_spec, constraints)

print(sched.to_string())

mod = generate_rtl(f_spec, sched)

assert(mod.name == f_spec.name)

generate_verilog(mod)


