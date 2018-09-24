import ast
from language import *
import bit_vector as b
import copy

from parser import *
from utils import *

class ScheduleConstraints:
    def __init__(self):
        self.num_cycles = 1
        self.resource_counts = {}

    def set_resource_count(self, resource_name, count):
        self.resource_counts[resource_name] = count

    def is_limited_unit(self, resource_name):
        return resource_name in self.resource_counts

    def available_units(self, resource_name):
        return self.resource_counts[resource_name]
    
class Schedule:
    def __init__(self):
        self.unique_num = 0
        self.functional_units = {}
        self.total_num_cycles = 0

    def num_cycles(self):
        return self.total_num_cycles

    def get_operation(self, name):
        return self.functional_units[name][0]
    
    def get_binding(self, instr):
        for func_name in self.functional_units:
            func = self.functional_units[func_name]
            sched = func[1]
            print('Checking', sched)
            for i in range(0, len(sched)):
                print('i =', i)
                it = sched[i]
                if it == instr:
                    return (func_name, i)

        print('Error: No binding for', instr)
        assert(False)

    def get_schedule(self, unit_name):
        return self.functional_units[unit_name][1]

    def to_string(self):
        s = '--- Schedule\n'
        for unit in self.functional_units:
            s += '\t' + unit + ' -> ' + str(self.functional_units[unit]) + '\n'
        return s

    def __repr__(self):
        return self.to_string()

    def __str__(self):
        return self.to_string()

    def bind_instruction(self, unit_name, start_time, instruction):
        unit = self.functional_units[unit_name]
        sched = self.get_schedule(unit_name)

        assert(len(sched) <= start_time)
        i = len(sched)
        while i < start_time:
            sched.append(None)
            i += 1
        sched.append(instruction)

    def fresh_name(self, prefix):
        n = prefix + '_' + str(self.unique_num)
        self.unique_num += 1
        return n

    def num_units_of_type(self, op_name):
        n = 0
        for u in self.functional_units:
            if self.get_operation(u).name == op_name:
                n += 1

        return n

    def get_functional_units(self):
        units = []
        for unit in self.functional_units:
            units.append((self.functional_units[unit][0],
                          self.functional_units[unit][1],
                          unit))

        return units

    def add_unit(self, unit):
        name = self.fresh_name(unit.name)
        self.functional_units[name] = (unit, [])
        return name

    def num_states(self):
        return 1

    def num_functional_units(self):
        return len(self.functional_units)

class Operation:
    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters

    def to_string(self):
        return 'Op[{0}]'.format(self.name)

    def __repr__(self):
        return self.to_string()

    def __str__(self):
        return self.to_string()

    def __eq__(self, other):
        if not isinstance(other, Operation):
            return False

        if (len(self.parameters) != len(other.parameters)):
            return False

        for i in range(0, len(self.parameters)):
            if self.parameters[i] != other.parameters[i]:
                return False
        return True

def op_string(op):
    if isinstance(op, ast.Invert):
        return 'invert'
    if isinstance(op, ast.Add):
        return 'add'
    if isinstance(op, ast.Eq):
        return 'eq'
    if isinstance(op, ast.LShift):
        return 'shl'
    if isinstance(op, ast.RShift):
        return 'lshr'
    if isinstance(op, ast.Sub):
        return 'sub'
    if isinstance(op, ast.Div):
        return 'unsigned_div'
    if isinstance(op, ast.Mult):
        return 'mult'
    if isinstance(op, ast.NotEq):
        return 'not_eq'

    print('Unsupported op =', op)

    assert(False)

sameWidthOps = [ast.Invert, ast.Add, ast.Sub]

def functional_unit(instr, f):
    if isinstance(instr, BinopInstr) and is_shift(instr):
        name = op_string(instr.op)
        l_width = f.symbol_type(instr.lhs).width()
        r_width = f.symbol_type(instr.rhs).width()
        name += '_' + str(l_width) + '_' + str(r_width)
        return Operation(name, [l_width, r_width])
        
    if isinstance(instr, BinopInstr) or isinstance(instr, UnopInstr):
        name = op_string(instr.op)
        width = f.symbol_type(instr.res).width()
        name += '_' + str(width)

        return Operation(name, [width])
    if isinstance(instr, CompareInstr):
        name = op_string(instr.op)
        in_width = f.symbol_type(instr.lhs).width()
        name += '_' + str(in_width)

        return Operation(name, [in_width])
    if isinstance(instr, AssignInstr):
        name = 'assign'
        in_width = f.symbol_type(instr.rhs).width()
        name += '_' + str(in_width)
        return Operation(name, [in_width])

    elif isinstance(instr, ConstBVDecl):
        name = 'constant_' + str(instr.value)
        return Operation(name, [instr.value])
    elif isinstance(instr, CallInstr) and isinstance(instr.func, ast.Name) and (instr.func.id == 'leading_zero_count'):

        print('lead zero args')
        for arg in instr.args:
            print(arg)
        assert(len(instr.args) == 1)

        width = f.symbol_type(instr.args[0]).width()
        return Operation(instr.func.id + '_' + str(width), [width])

    elif isinstance(instr, CallInstr) and isinstance(instr.func, ast.Name) and (instr.func.id == 'zero_extend'):

        assert(len(instr.args) == 2)

        out_width = f.get_int_constant_value(instr.args[0])
        in_width = f.symbol_type(instr.args[1]).width()
        return Operation(instr.func.id + '_' + str(out_width) + '_' + str(in_width), [out_width, in_width])
    elif isinstance(instr, CallInstr) and isinstance(instr.func, ast.Name) and (instr.func.id == 'concat'):
        assert(len(instr.args) == 2)

        in0_width = f.symbol_type(instr.args[0]).width()
        in1_width = f.symbol_type(instr.args[1]).width()
        return Operation(instr.func.id + '_' + str(in0_width) + '_' + str(in1_width), [in0_width, in1_width])
        
    elif isinstance(instr, CallInstr):
        assert(isinstance(instr.func, ast.Name))
        assert(False)

    elif isinstance(instr, TableLookupInstr):
        return Operation('builtin_table_lookup_' + instr.table_name, [f.symbol_type(instr.arg).width(), f.symbol_type(instr.res).width(), instr.table_name, f.get_module_name()])

    elif isinstance(instr, ITEInstr):
        width = f.symbol_type(instr.res).width()
        return Operation('ite_' + str(width), [width])
    elif isinstance(instr, SliceInstr):
        high_val = f.get_int_constant_value(instr.high)
        low_val = f.get_int_constant_value(instr.low)
        in_width = f.symbol_type(instr.value).width()
        return Operation('slice_' + str(in_width) + '_' + str(low_val) + '_' + str(high_val), [in_width, low_val, high_val])

    print('Unsupported functional unit', instr)
    assert(False)

def get_unit(op, constraints, s, cycle_time):
    num_units = s.num_units_of_type(op.name)
    print('# of units of type', op, '=', num_units)
    if not constraints.is_limited_unit(op.name) or s.num_units_of_type(op.name) < constraints.available_units(op.name):
        return s.add_unit(op)

    for unit in s.functional_units:
        n = s.get_operation(unit).name
        print('n = ', n)
        if n == op.name:
            unit_sched = s.get_schedule(unit)
            print('Unit sched =', unit_sched)
            if len(unit_sched) <= cycle_time:
                return unit

    print('Cannot schedule', op, 'at time', cycle_time)
    return None

# Simpler IR: Just have instruction resource pairs, or just instructions
# that respect the total resource counts available? Schedule is a list of lists
# of instructions? Then convert that to a schedule data structure once we are done?

# Note: Assumption is that we have zero delay, but possible resource limited units
def schedule(code_gen, f, constraints):
    s = Schedule()
    cycle_num = 0
    bound_instructions = set([])
    unbound_instructions = []
    for instr in f.instructions:
        unbound_instructions.append(instr)
        #set(f.instructions)

    cycle_time = 0

    while len(bound_instructions) < len(f.instructions):

        instr = next(iter(unbound_instructions))

        bound = True
        if not isinstance(instr, ReturnInstr) and not isinstance(instr, ConstDecl):
            opN = functional_unit(instr, f)
            op = opN.name

            unit_name = get_unit(functional_unit(instr, f), constraints, s, cycle_time)

            if unit_name == None:
                #print('Combinational schedule needs at least', units_used, 'of operation:', op, 'but only', constraints.available_units(op), 'are available. Adding a cycle')

                cycle_time += 1
                bound = False
            else:
                s.bind_instruction(unit_name, cycle_time, instr)
        else:
            bound_instructions.add(instr)

        if bound:
            bound_instructions.add(instr)
            unbound_instructions.pop(0)
            #unbound_instructions.remove(instr)

    s.total_num_cycles = cycle_time

    # Check that resource usage matches synthesis constraints
    total_resources = {}
    print('Units')
    for unit in s.functional_units:
        op_name = s.get_operation(unit).name
        if op_name in total_resources:
            total_resources[op_name] += 1
        else:
            total_resources[op_name] = 1

    print('Resources used')
    for r in total_resources:
        print('\t', r, ' -> ', total_resources[r])

    for r in constraints.resource_counts:
        max_val = constraints.resource_counts[r]
        if r in total_resources and max_val < total_resources[r]:
            print('Error: Too many uses of', r)
            print('r          =', r)
            print('max use    =', max_val)
            print('actual use =', total_resources[r])
            assert(False)

    return s
