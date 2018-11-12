import os

def tab(indent):
    s = ''
    for i in range(indent):
        s += '\t'

    return s

def has_prefix(name, prefix):
    return name[:len(prefix)] == prefix

def comma_list(strs):
    ls = ''
    for i in range(0, len(strs)):
        s = strs[i]
        ls += s
        if (i < len(strs) - 1):
            ls += ', '
        
    return ls



def run_cmd(cmd):
    res = os.system(cmd)
    return res == 0

def run_iverilog_test(mod_name):
    # Compile iverilogmod
    assert(run_cmd('iverilog -o {0} {0}.v ./verilog_tbs/{0}_tb.v'.format(mod_name)))
    assert(run_cmd('./{0} > {0}_res.txt'.format(mod_name)))

    f = open('{0}_res.txt'.format(mod_name), 'r')
    res = f.read()
    f.close()

    return res
