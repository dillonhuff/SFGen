from sfgen.bit_vector import *

def table_func(a):
    return a - bv_from_int(a.width(), 1)

def foo(a):
    res = lookup_in_table(a, table_func)

    return res
