class Module:
    def __init__(self, name):
        self.name = name

def generate_rtl(f, sched):
    mod = Module(f.name)

    return mod

def verilog_string(rtl_mod):
    return 'module {0}(); endmodule'.format(rtl_mod.name)

def generate_verilog(rtl_mod):
    f = open(rtl_mod.name + '.v', 'w')
    f.write(verilog_string(rtl_mod))
    f.close()
    return None
