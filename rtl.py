from utils import *

class Wire:
    def __init__(self, name, width):
        self.name = name
        self.width = width

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
        self.wires.append(Wire(name, width))
        self.in_ports.add(name)

    def in_port_names(self):
        return list(self.in_ports)

    
def generate_rtl(f, sched):
    mod = Module(f.name)

    for p in f.input_names():
        mod.add_in_port(p, f.symbol_type(p).width())

    return mod

def verilog_string(rtl_mod):
    
    return 'module {0}('.format(rtl_mod.name) + comma_list(rtl_mod.in_port_names()) + '); endmodule'

def generate_verilog(rtl_mod):
    f = open(rtl_mod.name + '.v', 'w')
    f.write(verilog_string(rtl_mod))
    f.close()
    return None
