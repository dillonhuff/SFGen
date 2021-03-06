import os
import os.path
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

from sfgen.verilog_backend import *
    
constraints = ScheduleConstraints()
synthesize_verilog('examples/table_lookup', 'foo', [l.ArrayType(4)], constraints)
