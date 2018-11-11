import ast
import sfgen.bit_vector as b
import copy
from sfgen.utils import *

class Type:
    def __init__(self):
        return None

class StructType(Type):
    def __init__(self, name, field_types, field_positions):
        self.name = name
        self.field_types = field_types
        self.field_positions = field_positions

    def get_field_at_position(self, position):
        assert(isinstance(position, int))

        for field in self.field_positions:
            if self.field_positions[field] == position:
                return field

        assert(False)
        
    def field_end_offset(self, field_name):
        assert(field_name in self.field_positions)
        assert(field_name in self.field_types)

        return self.field_start_offset(field_name) + self.field_types[field_name].width() - 1

    def width(self):
        w = 0
        for field in self.field_types:
            w += self.field_types[field].width()
        return w

    def field_start_offset(self, field_name):
        assert(field_name in self.field_positions)
        assert(field_name in self.field_types)

        pos = 0
        for i in range(0, self.field_positions[field_name]):
            field_i = self.get_field_at_position(i)
            pos += self.field_types[field_i].width()

        print('position of ', field_name, ' = ', pos)
        return pos
    
        #pos = field_positions[field_name]
        

    def to_string(self):
        return 'struct[{0}]({1})({2})'.format(self.name, self.field_types, self.field_positions)

    def __repr__(self):
        return self.to_string()

    def __str__(self):
        return self.to_string()

class IntegerType(Type):
    def __init__(self):
        Type.__init__(self)

    def __eq__(self, other):
        return isinstance(other, IntegerType)

    def to_string(self):
        return 'Z'

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

class FunctionType(Type):
    def __init__(self, arg_types, out_type):
        Type.__init__(self)
        self.arg_types = arg_types
        self.out_type = out_type

    def __eq__(self, other):
        if (not isinstance(other, ArrayType)):
            return False
        if self.out_type != other.out_type:
            return False

        if len(self.arg_types) != len(other.arg_types):
            return False

        for i in range(len(self.arg_types)):
            if self.arg_types[i] != other.arg_types[i]:
                return False
        return True

    def to_string(self):
        s = ''
        s += comma_list(list(map(lambda n : n.to_string(), self.arg_types)))
        s += ' -> ' + self.out_type.to_string()
        return '[' + str(self.w) + ']'

class ArrayType(Type):
    def __init__(self, w):
        Type.__init__(self)
        self.w = w

    def __eq__(self, other):
        if (not isinstance(other, ArrayType)):
            return False
        return self.w == other.w

    def width(self):
        return self.w

    def to_string(self):
        return '[' + str(self.w) + ']'

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

class LowInstruction:
    def __init__(self):
        return None

    def result_name(self):
        assert(False)

    def to_string(self):
        return 'UNKNOWN_INSTR'

    def __repr__(self):
        return self.to_string()

def is_width_call(func):
    return isinstance(func, ast.Attribute) and (func.attr == 'width')

def is_table_call(func):
    return isinstance(func, ast.Name) and (func.id == 'lookup_in_table')

class ITEInstr(LowInstruction):
    def __init__(self, res, test, true_exp, false_exp):
        self.res = res
        self.test = test
        self.true_exp = true_exp
        self.false_exp = false_exp

    def result_name(self):
        return self.res

    def arguments(self):
        return {self.test, self.true_exp, self.false_exp}

    def replace_values(self, f):
        self.res = f(self.res)
        self.test = f(self.test)
        self.true_exp = f(self.true_exp)
        self.false_exp = f(self.false_exp)
        
    def used_values(self):
        return {self.res, self.test, self.true_exp, self.false_exp}

    def to_string(self):
        return 'ite {0} {1} {2} {3}'.format(self.res, self.test, self.true_exp, self.false_exp)

class SliceInstr(LowInstruction):
    def __init__(self, res, value, low, high):
        self.res = res
        self.value = value
        self.low = low
        self.high = high

    def arguments(self):
        return {self.value, self.low, self.high}

    def result_name(self):
        return self.res
        
    def replace_values(self, f):
        self.res = f(self.res)
        self.value = f(self.value)
        self.low = f(self.low)        
        self.high = f(self.high)                

    def used_values(self):
        return {self.res, self.value, self.low, self.high}
        
    def to_string(self):
        return 'slice {0} {1} {2} {3}'.format(self.res, self.value, self.low, self.high)

class CompareInstr(LowInstruction):
    def __init__(self, op, res, lhs, rhs):
        self.op = op
        self.res = res
        self.lhs = lhs
        self.rhs = rhs

    def arguments(self):
        return {self.lhs, self.rhs}
    
    def result_name(self):
        return self.res
        
    def used_values(self):
        return {self.res, self.lhs, self.rhs}
        
    def to_string(self):
        return 'cmp {0} {1} {2}'.format(self.res, self.lhs, self.rhs)

    def replace_values(self, f):
        self.res = f(self.res)
        self.lhs = f(self.lhs)
        self.rhs = f(self.rhs)        

class TableLookupInstr(LowInstruction):
    def __init__(self, res, arg, table_name):
        self.res = res
        self.arg = arg
        self.table_name = table_name

    def result_name(self):
        return self.res
        
    def used_values(self):
        return {self.res, self.arg, self.table_name}
        
    def to_string(self):
        return 'lookup {0} {1} {2}'.format(self.res, self.arg, self.table_name)

    def arguments(self):
        return {self.arg, self.table_name}
    
    def replace_values(self, f):
        self.res = f(self.res)
        self.arg = f(self.arg)
        
class ConstDecl(LowInstruction):
    def __init__(self, res_name, num):
        self.res_name = res_name
        self.num = num

    def result_name(self):
        return self.res_name
        
    def replace_values(self, f):
        self.res_name = f(self.res_name)

    def arguments(self):
        return {}
        
    def used_values(self):
        return {self.res_name}
        
    def to_string(self):
        return 'const ' + self.res_name + ' ' + str(self.num)

class ConstBVDecl:
    def __init__(self, res_name, width, val):
        self.res_name = res_name
        self.value = b.bv_from_int(width, val)

    def arguments(self):
        return {}
        
    def result_name(self):
        return self.res_name
        
    def replace_values(self, f):
        self.res_name = f(self.res_name)
        
    def used_values(self):
        return {self.res_name}
        
    def to_string(self):
        return 'constbv ' + self.res_name + ' ' + str(self.value)

class AssignInstr(LowInstruction):
    def __init__(self, res, rhs):
        self.res = res
        self.rhs = rhs

    def arguments(self):
        return {self.rhs}
    
    def result_name(self):
        return self.res
        
    def replace_values(self, f):
        self.res = f(self.res)
        self.rhs = f(self.rhs)
        
    def used_values(self):
        return {self.res, self.rhs}
        
    def to_string(self):
        return 'assign {0} {1}'.format(self.res, self.rhs)

class ReadFieldInstr(LowInstruction):
    def __init__(self, res, struct, field):
        self.res = res
        self.struct = struct
        self.field = field

    def result_name(self):
        return self.res
        
    def replace_values(self, f):
        self.res = f(self.res)
        self.struct = f(self.struct)
        self.field = f(self.field)        

    def arguments(self):
        return {self.field, self.struct}
    
    def used_values(self):
        return {self.res, self.struct}
        
    def to_string(self):
        return 'read_field {0} {1}.{2}'.format(self.res, self.struct, self.field)
    
class ReturnInstr(LowInstruction):
    def __init__(self, name):
        self.val_name = name

    def result_name(self):
        return self.val_name
        
    def replace_values(self, f):
        self.val_name = f(self.val_name)

    def used_values(self):
        return {self.val_name}
        
    def to_string(self):
        return 'return ' + self.val_name

class BinopInstr(LowInstruction):
    def __init__(self, op, res, lhs, rhs):
        self.op = op
        self.res = res
        self.lhs = lhs
        self.rhs = rhs

    def result_name(self):
        return self.res

    def arguments(self):
        return {self.lhs, self.rhs}
    
    def replace_values(self, f):
        self.res = f(self.res)
        self.lhs = f(self.lhs)
        self.rhs = f(self.rhs)        
        
    def used_values(self):
        return {self.res, self.lhs, self.rhs}
        
    def to_string(self):
        return 'binop ' + str(self.op) + ' ' + self.res + ' ' + self.lhs + ' ' + self.rhs

class UnopInstr(LowInstruction):
    def __init__(self, op, res, in_name):
        self.op = op
        self.res = res
        self.in_name = in_name

    def result_name(self):
        return self.res

    def arguments(self):
        return {self.in_name}
    
    def replace_values(self, f):
        self.res = f(self.res)
        self.in_name = f(self.in_name)
        
    def used_values(self):
        return {self.res, self.in_name}
        
    def to_string(self):
        return 'unop ' + str(self.op) + ' ' + self.res + ' ' + self.in_name
        
class CallInstr(LowInstruction):
    def __init__(self, res, func, args):
        self.res = res
        self.func = func
        self.args = args

    def result_name(self):
        return self.res

    def arguments(self):
        arguments = set()
        for arg in self.args:
            arguments.add(arg)
        return arguments
    
    def replace_values(self, f):
        self.res = f(self.res)
        new_args = []
        for arg in self.args:
            new_args.append(f(arg))
        self.args = new_args

    def used_values(self):
        s = {self.res}
        for arg in self.args:
            s.add(arg)

        return s
        
    def to_string(self):
        if isinstance(self.func, str):
            s = 'call ' + self.res + ' ' + str(self.func) + ' '
        else:
            assert(isinstance(self.func, ast.Name))
            s = 'call ' + self.res + ' ' + str(self.func.id) + ' '
        arg_strs = []
        for a in self.args:
            arg_strs.append(str(a))
        s += comma_list(arg_strs)

        return s

class LowClassDef:
    def __init__(self, name, field_positions):
        self.name = name
        self.field_positions = field_positions

    def to_string(self):
        return 'class {0}({1})'.format(self.name, self.field_positions)

    def __repr__(self):
        return self.to_string()
    def __str__(self):
        return self.to_string()
        
class LowFunctionDef:
    def __init__(self, name, module_name, args):
        self.name = name
        self.module_name = module_name
        self.args = args
        self.instructions = []
        self.unique_num = 0
        self.symbol_table = {}
        self.output = None
        for arg in args:
            self.symbol_table[arg] = None

    def get_name(self):
        return self.name

    def get_module_name(self):
        return self.module_name

    def get_int_constant_value(self, name):
        for instr in self.instructions:
            if isinstance(instr, ConstDecl) and instr.res_name == name:
                return instr.num

        print('Cannot find constant', name)
        assert(False)
                
    def unique_suffix(self):
        suf = '_us_' + str(self.unique_num)
        self.unique_num += 1
        return suf

    def input_names(self):
        return self.args

    def get_arg(self, ind):
        assert(isinstance(ind, int))
        return self.args[ind]

    def symbol_type(self, name):
        if not name in self.symbol_table:
            print('Error: ', name, 'is not in symtab')
            
        assert(name in self.symbol_table)
        return self.symbol_table[name]

    def erase_symbol(self, name):
        del self.symbol_table[name]

    def set_symbol_type(self, name, tp):
        assert(isinstance(tp, Type))
        self.symbol_table[name] = tp
    
    def has_symbol(self, name):
        return name in self.symbol_table

    def add_instr(self, instr):
        assert(self.output == None)
        self.instructions.append(instr)
        if (isinstance(instr, ReturnInstr)):
            self.output = instr.val_name

    def output_name(self):
        return self.output

    def add_symbol(self, name, tp):
        self.symbol_table[name] = tp

    def fresh_sym(self):
        name = "fs_" + str(self.unique_num)
        self.unique_num += 1
        self.add_symbol(name, None)
        return name
        
    def to_string(self):
        s = 'symbols\n';
        for sym in self.symbol_table:
            s += '\t' + sym + ' -> ' + str(self.symbol_table[sym]) + '\n'
        s += 'endsymbols\n\n'
        s += 'function ' + self.name + '('
        s += comma_list(self.args) + ')\n'
        for instr in self.instructions:
            s += '\t' + instr.to_string() + '\n'
        s += 'end'
        return s
