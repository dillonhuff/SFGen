from rtl import *

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
        elif has_prefix(rtl_mod.name, 'builtin_mux_'):
            width = rtl_mod.get_parameter('width')
            depth = rtl_mod.get_parameter('depth')
            sel_width = storage_width(depth) #math.ceil(math.log2(depth)) + 1

            mod_str += '\treg [{0}:0] {1};\n'.format(width - 1, 'out_reg')
            mod_str += '\talways @(*) begin\n'
            mod_str += '\t\tcase(sel)\n'
            for i in range(depth):
                arg = bit_vector.bv_from_int(sel_width, i)
                mod_str += "\t\t\t{0}'b{1}: out_reg = in{2};\n".format(sel_width, arg, i)
            mod_str += '\t\tendcase\t\n'
            mod_str += '\tend\n'
            mod_str += '\tassign out = out_reg;\n'
        elif has_prefix(rtl_mod.name, 'builtin_counter'):
            num_stages = rtl_mod.get_parameter('num_stages')
            width = storage_width(num_stages)
            mod_str += '\treg [{0}:0] {1};\n'.format(width - 1, 'stage_num')
            mod_str += '\talways @(posedge clk) begin\n'
            mod_str += '\t\tif (rst) begin\n'
            mod_str += '\t\t\tstage_num <= 0;\n'
            mod_str += '\t\tend else if (stage_num == {0}) begin\n'.format(num_stages - 1)
            mod_str += '\t\t\tstage_num <= 0;\n'
            mod_str += '\t\tend else begin\n'
            mod_str += '\t\t\tstage_num <= stage_num + 1;\n'
            mod_str += '\t\tend\n'            
            mod_str += '\tend\n'            
            mod_str += '\tassign out = stage_num;\n'
        elif has_prefix(rtl_mod.name, 'builtin_fifo'):
            delay = rtl_mod.get_parameter('delay')
            width = rtl_mod.get_parameter('width')

            current_out = 'in'
            for i in range(delay):
                next_out = 'delay_reg_{0}'.format(i)
                mod_str += '\treg [{0}:0] {1};\n'.format(width - 1, next_out)
                mod_str += '\talways @(posedge clk) begin\n'
                mod_str += '\t\t{0} <= {1};\n'.format(next_out, current_out)
                mod_str += '\tend\n'
                current_out = next_out

            mod_str += '\tassign out = {0};\n'.format(current_out)
        else:
            print('Error: Unsupported builtin', rtl_mod.name)
            assert(False)
    else:
        for cell in rtl_mod.cells:
            #print('Cell =', cell)
            mod_str += '\t' + cell[0].name + ' ' + cell[2] + '(' + comma_list(verilog_port_connections(cell[1], cell[0])) + ');\n'

    mod_str += '\nendmodule\n\n'

    return mod_str

def generate_verilog(rtl_mod):
    f = open(rtl_mod.name + '.v', 'w')
    f.write(verilog_string(rtl_mod))
    f.close()
    return None
