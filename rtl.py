from utils import *
import language as l
import parser as p
import ast
import importlib
import bit_vector
from scheduling import *
import math

def storage_width(w):
    return math.ceil(math.log2(w))

class Wire:
    def __init__(self, name, width, is_in=False, is_out=False, is_reg=False):
        self.name = name
        self.width = width
        self.is_register = is_reg
        if is_in or is_out:
            self.is_port = True
            if is_in:
                self.is_in = True
            else:
                self.is_in = False
        else:
            self.is_port = False

    def is_reg(self):
        return is_register

    def is_input(self):
        return self.is_port and self.is_in

    def to_string(self):
        return '{0} : [{1}]'.format(self.name, self.width)

    def __repr__(self):
        return self.to_string()

    def __str__(self):
        return self.to_string()
    
    def is_output(self):
        return self.is_port and (not self.is_in)

def binop_module(name, width):
    m = Module('builtin_{0}_{1}'.format(name, width))
    m.add_in_port('in0', width)
    m.add_in_port('in1', width)
    m.add_out_port('out', width)
    return m

def module_for_functional_unit(unit):
    if (has_prefix(unit.name, 'add_')):
        return binop_module(unit.name, unit.parameters[0])

    if (has_prefix(unit.name, 'mult_')):
        return binop_module(unit.name, unit.parameters[0])        
    
    if (has_prefix(unit.name, 'unsigned_div_')):
        return binop_module(unit.name, unit.parameters[0])                
    
    if (has_prefix(unit.name, 'sub_')):
        return binop_module(unit.name, unit.parameters[0])
    
    if (has_prefix(unit.name, 'assign_')):
        width = unit.parameters[0]
        m = Module('builtin_assign_' + str(width))
        m.add_in_port('in', width)
        m.add_out_port('out', width)
        return m

    if (has_prefix(unit.name, 'ite_')):
        width = unit.parameters[0]
        m = Module('builtin_ite_' + str(width))

        m.add_in_port('in0', width)
        m.add_in_port('in1', width)
        m.add_in_port('sel', 1)        
        m.add_out_port('out', width)
        return m
    
    if (has_prefix(unit.name, 'eq_')):
        width = unit.parameters[0]
        m = Module('builtin_eq_' + str(width))
        m.add_in_port('in0', width)
        m.add_in_port('in1', width)
        m.add_out_port('out', 1)
        return m

    if (has_prefix(unit.name, 'not_eq_')):
        width = unit.parameters[0]
        m = Module('builtin_not_eq_' + str(width))
        m.add_in_port('in0', width)
        m.add_in_port('in1', width)
        m.add_out_port('out', 1)
        return m
    
    if (has_prefix(unit.name, 'zero_extend_')):
        out_width = unit.parameters[0]
        in_width = unit.parameters[1]

        m = Module('builtin_zero_extend_' + str(out_width) + '_' + str(in_width))
        m.add_parameter('out_width', out_width)
        m.add_parameter('in_width', in_width)

        m.add_in_port('in', in_width)
        m.add_out_port('out', out_width)
        return m
    
    if (has_prefix(unit.name, 'invert_')):
        width = unit.parameters[0]
        m = Module('builtin_invert_' + str(width))
        m.add_in_port('in', width)
        m.add_out_port('out', width)
        return m

    if (has_prefix(unit.name, 'constant_')):
        value = unit.parameters[0]
        width = value.width()
        m = Module('builtin_constant_' + str(width) + '_' + str(value))
        m.add_parameter("value", value)
        m.add_in_port('in', width)
        m.add_out_port('out', width)
        return m

    if (has_prefix(unit.name, 'slice_')):
        in_width = unit.parameters[0]
        start_ind = unit.parameters[1]
        end_ind = unit.parameters[2]
        m = Module('builtin_slice_' + str(in_width) + '_' + str(start_ind) + '_' + str(end_ind))

        m.add_parameter("start", start_ind)
        m.add_parameter("end", end_ind)
        
        m.add_in_port('in', in_width)
        m.add_out_port('out', (end_ind - start_ind + 1))
        return m

    if (has_prefix(unit.name, 'shl_')):
        width0 = unit.parameters[0]
        width1 = unit.parameters[1]
        m = Module('builtin_shl_' + str(width0) + '_' + str(width1))

        m.add_in_port('in0', width0)
        m.add_in_port('in1', width1)
        m.add_out_port('out', width0)

        return m

    if (has_prefix(unit.name, 'lshr_')):
        width0 = unit.parameters[0]
        width1 = unit.parameters[1]
        m = Module('builtin_lshr_' + str(width0) + '_' + str(width1))

        m.add_in_port('in0', width0)
        m.add_in_port('in1', width1)
        m.add_out_port('out', width0)

        return m

    if (has_prefix(unit.name, 'leading_zero_count_')):
        width = unit.parameters[0]
        m = Module('builtin_leading_zero_count_' + str(width))
        m.add_parameter('width', width)

        m.add_in_port('in', width)
        m.add_out_port('out', width)

        return m

    if (has_prefix(unit.name, 'concat_')):
        width0 = unit.parameters[0]
        width1 = unit.parameters[1]
        m = Module('builtin_concat_' + str(width0) + '_' + str(width1))

        m.add_in_port('in0', width0)
        m.add_in_port('in1', width1)
        m.add_out_port('out', width0 + width1)

        return m

    if (has_prefix(unit.name, 'builtin_table_lookup_')):
        in_width = unit.parameters[0]
        out_width = unit.parameters[1]

        table_name = unit.parameters[2]
        module_name = unit.parameters[3]

        m = Module('builtin_table_lookup_{0}_{1}_{2}'.format(table_name, in_width, out_width))

        m.add_in_port('in', in_width)
        m.add_out_port('out', out_width)

        m.add_parameter('table_name', table_name)
        m.add_parameter('module_name', module_name)
        m.add_parameter('in_width', in_width)
        m.add_parameter('out_width', out_width)        

        return m

    
    print('Non builtin functional unit:', unit.name, unit.parameters)

    m = Module(unit.name)
    arg_widths = unit.parameters
    m.add_parameter('args', unit.parameters)
    for param in unit.parameters:
        param_name = param[0]
        param_type = param[1]

        m.add_in_port(param_name, param_type)

    # TODO: Fix this temporary hack
    m.add_parameter('output_name', ('out', 32))
    m.add_out_port('out', 32)

    return m
    
    #assert(False)

def get_port_map(i0, cell_module):
    wire_connections = {}
    if isinstance(i0, p.BinopInstr):
        wire_connections['in0'] = [i0.lhs]
        wire_connections['in1'] = [i0.rhs]
        wire_connections['out'] = [i0.res]

    elif isinstance(i0, p.ITEInstr):
        wire_connections['in0'] = [i0.false_exp]
        wire_connections['in1'] = [i0.true_exp]
        wire_connections['sel'] = [i0.test]
        wire_connections['out'] = [i0.res]
            
    elif isinstance(i0, p.UnopInstr):
        wire_connections['in'] = [i0.in_name]
        wire_connections['out'] = [i0.res]
    elif  isinstance(i0, p.SliceInstr):
        wire_connections['in'] = [i0.value]
        wire_connections['out'] = [i0.res]

    elif isinstance(i0, p.AssignInstr):
        wire_connections['in'] = [i0.rhs]
        wire_connections['out'] = [i0.res]

    elif isinstance(i0, p.CompareInstr):
        wire_connections['in0'] = [i0.lhs]
        wire_connections['in1'] = [i0.rhs]           
        wire_connections['out'] = [i0.res]

    elif isinstance(i0, p.TableLookupInstr):
        wire_connections['in'] = [i0.arg]
        wire_connections['out'] = [i0.res]

    elif isinstance(i0, p.ConstBVDecl):
        wire_connections['out'] = [i0.res_name]
    elif isinstance(i0, p.CallInstr) and isinstance(i0.func, ast.Name):
        if i0.func.id == 'leading_zero_count':
            wire_connections['in'] = [i0.args[0]]
            wire_connections['out'] = [i0.res]
        elif i0.func.id == 'zero_extend':
            wire_connections['in'] = [i0.args[1]]
            wire_connections['out'] = [i0.res]

        elif i0.func.id == 'concat':
            wire_connections['in0'] = [i0.args[0]]
            wire_connections['in1'] = [i0.args[1]]
            wire_connections['out'] = [i0.res]

        else:
            print('Unrecognized function', i0.func.id)
            assert(False)

    elif i0 == None:
        for in_port in cell_module.in_port_names():
            wire_connections[in_port] = [None]
        for out_port in cell_module.out_port_names():
            wire_connections[out_port] = [None]

    else:
        assert(isinstance(i0, p.CallInstr))
        i = 0
        print('Attaching args')
        for arg in cell_module.get_parameter('args'):
            print('i0[args] =', i0.args[i])
            wire_connections[arg[0]] = [i0.args[i]]
            i += 1

        # TODO: Add real output port naming
        output_info = cell_module.get_parameter('output_name')
        out_name = output_info[0]
        out_width = output_info[1]
        wire_connections[out_name] = [i0.result_name()]

    return wire_connections
    
def build_module_connections(cell_module, bound_instructions, cell_name):
    wire_connections = {}

    for i0 in bound_instructions:

        i_conns = get_port_map(i0, cell_module)
        for val in i_conns:
            if val in wire_connections:
                for conn in i_conns[val]:
                    wire_connections[val].append(conn)
            else:
                wire_connections[val] = i_conns[val]

    return wire_connections
        
class Module:
    def __init__(self, name):
        self.name = name
        self.parameters = {}
        self.unique_num = 0
        self.wires = []
        self.in_ports = set([])
        self.out_ports = set([])
        self.cells = []

    def build_x_constant(self, width):
        mod_name = self.fresh_name('x_const')
        out_name = self.fresh_name('undefined_value')
        self.add_wire(out_name, width)
        val = bit_vector.unknown_bits(width)
        const_mod = Module('builtin_constant_' + str(width) + '_' + str(val))
        const_mod.add_out_port('out', width)
        const_mod.add_parameter('value', val)
        const_mod.add_parameter('width', width)
        self.add_cell(const_mod, [('out', out_name)], mod_name)
        return out_name

    def add_fifo(self, delay, width, output, inp, clk):
        cell_mod = Module('builtin_fifo_{0}_{1}'.format(delay, width))
        cell_mod.add_parameter('delay', delay)
        cell_mod.add_parameter('width', width)

        cell_mod.add_in_port('in', width)
        cell_mod.add_in_port('clk', 1)
        cell_mod.add_out_port('out', width)
        
        conns = [('in', inp), ('out', output), ('clk', clk)]
        n = self.fresh_name('fifo')
        self.add_cell(cell_mod, conns, n)

    def add_assign(self, res_name, rhs_name, width):
        cell_mod = module_for_functional_unit(Operation('assign_' + str(width), [width]))

        in_wire = rhs_name #Wire(rhs_name, width)
        res_wire = res_name #Wire(res_name, width)
        self.add_cell(cell_mod, [('in', in_wire), ('out', res_wire)], 'fresh_assign_' + str(self.unique_num))
        self.unique_num += 1
        
    def add_parameter(self, name, value):
        self.parameters[name] = value

    def get_parameter(self, name):
        return self.parameters[name]
    
    def all_cells(self):
        return self.cells

    def get_wire_width(self, name):
        for w in self.wires:
            if w.name == name:
                return w.width


        assert(False)

    def add_cell(self, cell_module, wire_connections, cell_name):
        self.cells.append((cell_module, wire_connections, cell_name))

    def fresh_name(self, prefix):
        n = prefix + '_' + str(self.unique_num)
        self.unique_num += 1
        return n

    def fresh_wire(self, width):
        n = 'fresh_wire_' + str(self.unique_num)
        self.unique_num += 1
        self.add_wire(n, width)
        return n

    def add_wire(self, name, width):
        self.wires.append(Wire(name, width, False, False, False))

    def add_reg(self, name, width):
        self.wires.append(Wire(name, width, False, False, True))
        
    def add_in_port(self, name, width):
        self.wires.append(Wire(name, width, True, False, False))
        self.in_ports.add(name)

    def add_out_port(self, name, width):
        self.wires.append(Wire(name, width, False, True, False))
        self.out_ports.add(name)
        
    def in_port_names(self):
        return list(self.in_ports)

    def out_port_names(self):
        return list(self.out_ports)

def build_mux(sched, container_module, connected_inputs, output_to, width):
    print('mux inputs =', connected_inputs)
    mux_mod = Module('builtin_mux_' + str(len(connected_inputs)) + '_' + str(width))

    mux_mod.add_parameter('depth', len(connected_inputs))
    mux_mod.add_parameter('width', width)

    wire_connections = []
    wire_connections.append(('sel', 'global_stage_counter'))
    for i in range(len(connected_inputs)):
        mux_mod.add_in_port('in' + str(i), width)
        next_in = connected_inputs[i]
        if next_in != None:

            produced_time = 0
            if not next_in in container_module.in_port_names():
                produced_time = sched.production_time(next_in)
            next_in_w = container_module.fresh_wire(width)

            assert(produced_time <= i)
            
            container_module.add_fifo(i - produced_time, width, next_in_w, next_in, 'clk')
            wire_connections.append(('in' + str(i), next_in_w))
        else:
            x_const = container_module.build_x_constant(width)
            wire_connections.append(('in' + str(i), x_const))

    mux_mod.add_in_port('sel', storage_width(len(connected_inputs)))
    mux_mod.add_out_port('out', width)

    out_w = container_module.fresh_wire(width)
    wire_connections.append(('out', out_w))
    container_module.add_cell(mux_mod, wire_connections, container_module.fresh_name('in_mux'))
    return out_w

def generate_rtl(f, sched):
    mod = Module(f.name)

    for sym in f.symbol_table:
        if sym in f.input_names():
            mod.add_in_port(sym, f.symbol_type(sym).width())
        elif sym == f.output_name():
            mod.add_out_port(f.output_name(), f.symbol_type(f.output_name()).width())
        elif isinstance(f.symbol_type(sym), l.ArrayType):
            mod.add_wire(sym, f.symbol_type(sym).width())

    arg_params = []
    for arg in f.args:
        # TODO: This should be assert(False), symbol table should cull unused
        # symbols after specialization
        if f.has_symbol(arg):
            arg_params.append((arg, f.symbol_type(arg).width()))
    mod.add_parameter('args', arg_params)
    mod.add_parameter('output_name', (f.output_name(), f.symbol_type(f.output_name()).width()))

    if sched.num_cycles() > 1:
        stage_width = storage_width(sched.num_cycles()) #math.ceil(math.log2(sched.num_cycles())) + 1
        mod.add_reg('global_stage_counter', stage_width)
        mod.add_in_port('clk', 1)
        mod.add_in_port('en', 1)
        
        counter_mod = Module('builtin_counter_' + str(stage_width))
        counter_mod.add_parameter('num_stages', sched.num_cycles())
        counter_mod.add_in_port('clk', 1)
        counter_mod.add_in_port('rst', 1)        
        counter_mod.add_out_port('out', stage_width)
        
        mod.add_cell(counter_mod, [('clk', 'clk'), ('rst', 'en'), ('out', 'global_stage_counter')], 'stage_counter')

    mod_map = {}
    for sub_name in sched.subschedules:
        sub = sched.subschedules[sub_name]
        sub_f = sub.function
        assert(isinstance(sub_f, LowFunctionDef))
        
        f_mod = generate_rtl(sub_f, sub)
        mod_map[f_mod.name] = f_mod

    print('Mod map')
    for submodule in mod_map:
        print('Mod =', submodule)
        
    for unit in sched.get_functional_units():
        print('Unit = ', unit)
        unit_type = unit[0]
        cell_name = unit[2]
        unit_sched = sched.get_schedule(cell_name)

        print('sched      = ', unit_sched)
        print('len(sched) = ', len(unit_sched))

        if unit_type.name in mod_map:
            mod_fu = mod_map[unit_type.name]
        else:
            mod_fu = module_for_functional_unit(unit_type)

        wire_connection_map = build_module_connections(mod_fu, unit_sched, cell_name)

        print('Wire connection map =', wire_connection_map)
        mux_to_output_connections = []
        driven_by_output = []

        wire_connections = []

        # Assemble the input port muxes
        for port in wire_connection_map:
            connected_wires = wire_connection_map[port]

            if port in mod_fu.in_port_names():

                if len(connected_wires) > 1:
                    res_wire = build_mux(sched, mod, connected_wires, port, mod_fu.get_wire_width(port))
                    wire_connections.append((port, res_wire))
                else:
                    wire_connections.append((port, connected_wires[0]))

            else:
                print('port =', port)
                assert(port in mod_fu.out_port_names())
                out_w = mod.fresh_wire(mod_fu.get_wire_width(port))

                wire_connections.append((port, out_w))
            
                for out_wire in connected_wires:
                    if out_wire != None:
                        mod.add_assign(out_wire, out_w, mod.get_wire_width(out_w))

        mod.add_cell(mod_fu, wire_connections, cell_name)

    return mod
