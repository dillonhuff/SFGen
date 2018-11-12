from parser import *
import language as l
import ast
from rtl import *
from scheduling import *
from utils import *
from verilog_backend import *

code_gen = codegen_for_module('table_lookup')    
f_spec = specialize_types(code_gen, 'foo', [l.ArrayType(4)])

constraints = ScheduleConstraints()
sched = schedule(code_gen, f_spec, constraints)

print(sched.to_string())

mod = generate_rtl(f_spec, sched)

assert(mod.name == f_spec.name)

generate_verilog(mod)
