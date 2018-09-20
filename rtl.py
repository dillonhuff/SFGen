from utils import *
import language as l
import parser as p
import ast
import importlib
import bit_vector
from scheduling import *

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

def module_for_functional_unit(unit):
    if (has_prefix(unit.name, 'add_')):
        width = unit.parameters[0]
        m = Module('builtin_add_' + str(width))
        m.add_in_port('in0', width)
        m.add_in_port('in1', width)
        m.add_out_port('out', width)
        return m

    if (has_prefix(unit.name, 'mult_')):
        width = unit.parameters[0]
        m = Module('builtin_mult_' + str(width))
        m.add_in_port('in0', width)
        m.add_in_port('in1', width)
        m.add_out_port('out', width)
        return m
    
    if (has_prefix(unit.name, 'unsigned_div_')):
        width = unit.parameters[0]
        m = Module('builtin_unsigned_div_' + str(width))
        m.add_in_port('in0', width)
        m.add_in_port('in1', width)
        m.add_out_port('out', width)
        return m
    
    if (has_prefix(unit.name, 'sub_')):
        width = unit.parameters[0]
        m = Module('builtin_sub_' + str(width))
        m.add_in_port('in0', width)
        m.add_in_port('in1', width)
        m.add_out_port('out', width)
        return m
    
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
    print('Error: Unsupported functional unit:', unit.name, unit.parameters)
    assert(False)

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
         print('No connections for instruction', i0)
         assert(False)

    return wire_connections
    
def build_module_connections(cell_module, bound_instructions, cell_name):
    wire_connections = {}

    for i0 in bound_instructions:
        i0 = bound_instructions[0]
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

def generate_rtl(f, sched):
    mod = Module(f.name)

    for sym in f.symbol_table:
        if sym in f.input_names():
            mod.add_in_port(sym, f.symbol_type(sym).width())
        elif sym == f.output_name():
            mod.add_out_port(f.output_name(), f.symbol_type(f.output_name()).width())
        elif isinstance(f.symbol_type(sym), l.ArrayType):
            mod.add_wire(sym, f.symbol_type(sym).width())

    for unit in sched.get_functional_units():
        print('Unit = ', unit)
        unit_type = unit[0]
        cell_name = unit[2]
        unit_sched = sched.get_schedule(cell_name)

        print('sched      = ', unit_sched)
        print('len(sched) = ', len(unit_sched))

        mod_fu = module_for_functional_unit(unit_type)
        wire_connection_map = build_module_connections(mod_fu, unit_sched, cell_name)

        mux_to_output_connections = []
        driven_by_output = []

        wire_connections = []

        # Assemble the input port muxes
        for port in wire_connection_map:
            connected_wires = wire_connection_map[port]

            if port in mod_fu.in_port_names():
                
                for in_wire in connected_wires:
                    wire_connections.append((port, in_wire))
                
            else:
                assert(port in mod_fu.out_port_names())
                out_w = mod.fresh_wire(mod_fu.get_wire_width(port))

                wire_connections.append((port, out_w))
            
                for out_wire in connected_wires:
                    mod.add_assign(out_wire, out_w, mod.get_wire_width(out_w))

        mod.add_cell(mod_fu, wire_connections, cell_name)

    return mod

def verilog_wire_decls(rtl_mod):
    decls = ''
    for w in rtl_mod.wires:
        if w.is_input():
            decls += '\tinput [' + str(w.width - 1) + ':0] ' + w.name + ';\n'
        elif w.is_output():
            decls += '\toutput [' + str(w.width - 1) + ':0] ' + w.name + ';\n'
        else:
            decls += '\twire [' + str(w.width - 1) + ':0] ' + w.name + ';\n'
    return decls

def verilog_port_connections(input_schedule, module):
    print('Input schedule for', module)
    for i in input_schedule:
        print('\t', i)

    #assert(len(input_schedule) == 1)
    
    conn_strings = list(map(lambda x: '.{0}({1})'.format(x[0], x[1]), input_schedule))
    return conn_strings

def lead_zero_body(width):
    s = ""
    s += "\treg [" + str(width - 1) + ":0] out_reg;\n";
    s += "\talways @(*) begin\n";
    s += "\t\tcasez(in)\n";
    for i in range(0, width):
        inPattern = ""
        for pre in range(0, i):
            inPattern += '0'

        inPattern += '1';

        for post in range(i + 1, width):
            inPattern += '?'

        res = str(i);
        s += "\t\t\t" + str(width) + "'b" + inPattern + ": out_reg = " + str(i) + ";\n"

    s += "\t\tendcase\n";
    s += "\tend\n";
    s += "\tassign out = out_reg;\n";

    return s
    
def verilog_string(rtl_mod):

    mod_str = ''
    used_mods = set()
    for cell in rtl_mod.all_cells():
        mod = cell[0]
        if not mod.name in used_mods:
            used_mods.add(mod.name)
            mod_str += verilog_string(mod)
    
    mod_str += 'module {0}('.format(rtl_mod.name) + comma_list(rtl_mod.in_port_names() + rtl_mod.out_port_names()) + ');\n'
    mod_str += verilog_wire_decls(rtl_mod)

    mod_str += '\n'

    if has_prefix(rtl_mod.name, 'builtin_'):
        if has_prefix(rtl_mod.name, 'builtin_add_'):
            mod_str += '\tassign out = in0 + in1;\n'

        elif has_prefix(rtl_mod.name, 'builtin_mult_'):
            mod_str += '\tassign out = in0 * in1;\n'

        elif has_prefix(rtl_mod.name, 'builtin_unsigned_div_'):
            mod_str += '\tassign out = in0 / in1;\n'
            
        elif has_prefix(rtl_mod.name, 'builtin_sub_'):
            mod_str += '\tassign out = in0 - in1;\n'
            
        elif has_prefix(rtl_mod.name, 'builtin_shl_'):
            mod_str += '\tassign out = in0 << in1;\n'

        elif has_prefix(rtl_mod.name, 'builtin_lshr_'):
            mod_str += '\tassign out = in0 >> in1;\n'
            
        elif has_prefix(rtl_mod.name, 'builtin_eq_'):
            mod_str += '\tassign out = in0 == in1;\n'

        elif has_prefix(rtl_mod.name, 'builtin_not_eq_'):
            mod_str += '\tassign out = in0 != in1;\n'
            
        elif has_prefix(rtl_mod.name, 'builtin_assign_'):
            mod_str += '\tassign out = in;\n'

        elif has_prefix(rtl_mod.name, 'builtin_ite_'):
            mod_str += '\tassign out = sel ? in1 : in0;\n'
            
        elif has_prefix(rtl_mod.name, 'builtin_invert_'):
            mod_str += '\tassign out = ~in;\n'

        elif has_prefix(rtl_mod.name, 'builtin_zero_extend_'):
            out_width = rtl_mod.get_parameter('out_width')
            in_width = rtl_mod.get_parameter('in_width')

            assert(out_width >= in_width)
            mod_str += "\tassign out = {{(" + str(out_width) + " - " + str(in_width) + "){1'b0}}, in};\n"
            
        elif has_prefix(rtl_mod.name, 'builtin_leading_zero_count_'):
            mod_str += lead_zero_body(rtl_mod.get_parameter('width'))
            
        elif has_prefix(rtl_mod.name, 'builtin_constant_'):
            val = rtl_mod.get_parameter("value")
            width = val.width()
            mod_str += '\tassign out = ' + str(width) + "'b" + str(rtl_mod.get_parameter("value")) + ';\n'

        elif has_prefix(rtl_mod.name, 'builtin_slice_'):
            start = rtl_mod.get_parameter("start")
            end = rtl_mod.get_parameter("end")
            mod_str += '\tassign out = in[{0}:{1}];\n'.format(end, start)

        elif has_prefix(rtl_mod.name, 'builtin_concat_'):
            mod_str += '\tassign out = {in0, in1};\n'

        elif has_prefix(rtl_mod.name, 'builtin_table_lookup_'):

            table_name = rtl_mod.get_parameter('table_name')

            # NOTE: Assumes the module is huang divider!!
            mod_name = rtl_mod.get_parameter('module_name')
            mod = importlib.import_module(mod_name)
            table_function = getattr(mod, table_name)
            
            in_width = rtl_mod.get_parameter('in_width')
            out_width = rtl_mod.get_parameter('out_width')
            
            mod_str += '\treg [{0}:0] {1};\n'.format(out_width - 1, 'out_reg')
            mod_str += '\talways @(*) begin\n'
            mod_str += '\t\tcase(in)\n'
            for i in range(0, pow(2, in_width)):
                arg = bit_vector.bv_from_int(in_width, i)
                res = bit_vector.bv_from_int(out_width, 0)
                mod_str += "\t\t\t{0}'b{1}: out_reg = {2}'b{3};\n".format(in_width, arg, out_width, table_function(arg))
            mod_str += '\t\tendcase\n'
            mod_str += '\tend\n'            
            mod_str += '\tassign out = out_reg;\n';
            
        else:
            print('Error: Unsupported builtin', rtl_mod.name)
            assert(False)
    else:
        for cell in rtl_mod.cells:
            print('Cell =', cell)
            mod_str += '\t' + cell[0].name + ' ' + cell[2] + '(' + comma_list(verilog_port_connections(cell[1], cell[0])) + ');\n'

    mod_str += '\nendmodule\n\n'

    return mod_str

def generate_verilog(rtl_mod):
    f = open(rtl_mod.name + '.v', 'w')
    f.write(verilog_string(rtl_mod))
    f.close()
    return None
