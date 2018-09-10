from utils import *

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

class Module:
    def __init__(self, name):
        self.name = name
        self.unique_num = 0
        self.wires = []
        self.in_ports = set([])
        self.out_ports = set([])

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

    for p in f.input_names():
        mod.add_in_port(p, f.symbol_type(p).width())

    mod.add_out_port(f.output_name(), f.symbol_type(f.output_name()).width())

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
    
    mod_str = 'module {0}('.format(rtl_mod.name) + comma_list(rtl_mod.in_port_names() + rtl_mod.out_port_names()) + ');\n'
    mod_str += verilog_wire_decls(rtl_mod)
    mod_str += '\nendmodule'

    return mod_str

def generate_verilog(rtl_mod):
    f = open(rtl_mod.name + '.v', 'w')
    f.write(verilog_string(rtl_mod))
    f.close()
    return None
