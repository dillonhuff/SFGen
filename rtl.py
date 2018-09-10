from utils import *
import language as l

class Wire:
    def __init__(self, name, width, is_in, is_out):
        self.name = name
        self.width = width
        if is_in or is_out:
            self.is_port = True
            if is_in:
                self.is_in = True
            else:
                self.is_in = False
        else:
            self.is_port = False

    def is_input(self):
        return self.is_port and self.is_in

    def is_output(self):
        return self.is_port and (not self.is_in)

class Cell:
    def __init__(self):
        return None

def module_for_functional_unit(unit):
    if (has_prefix(unit.name, 'add_')):
        width = unit.parameters[0]
        m = Module('add_' + str(width))
        m.add_in_port('in0', width)
        m.add_in_port('in1', width)
        m.add_out_port('out', width)
        return m

    if (has_prefix(unit.name, 'invert_')):
        width = unit.parameters[0]
        m = Module('invert_' + str(width))
        m.add_in_port('in', width)
        m.add_out_port('out', width)
        return m

    print('Error: Unsupported functional unit:', unit.name)
    assert(False)
    
class Module:
    def __init__(self, name):
        self.name = name
        self.unique_num = 0
        self.wires = []
        self.in_ports = set([])
        self.out_ports = set([])
        self.cells = []

    def all_cells(self):
        return self.cells
    
    def add_cell(self, cell_module, port_connections, cell_name):
        wire_connections = []
        self.cells.append((cell_module, wire_connections, cell_name))

    def add_wire(self, name, width):
        self.wires.append(Wire(name, width, False, False))

    def add_in_port(self, name, width):
        self.wires.append(Wire(name, width, True, False))
        self.in_ports.add(name)

    def add_out_port(self, name, width):
        self.wires.append(Wire(name, width, False, True))
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

    assert(sched.num_cycles() == 0)

    for unit in sched.get_functional_units():
        mod.add_cell(module_for_functional_unit(unit[0]), unit[1], unit[2])
    # for instr in f.instructions:
    #     # Look up the functional unit
    #     # Connect to the appropriate port and cycle of the unit
        
    #     None
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

    for cell in rtl_mod.cells:
        mod_str += '\t' + cell[0].name + ' ' + cell[2] + '();\n'
    mod_str += '\nendmodule\n\n'

    return mod_str

def generate_verilog(rtl_mod):
    f = open(rtl_mod.name + '.v', 'w')
    f.write(verilog_string(rtl_mod))
    f.close()
    return None
