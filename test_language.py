from bit_vector import *
from language import *

def build_tc_negate(width):
    assert(isinstance(width, int))
    
    f = new_function("f", Variable("out", ArrayType(width)))
    f.add_input("in", width)

    assert(len(f.get_formal_args()) == 1)
    
    f.add_assign(f.get("out"), ~f.get("in") + const(width, 1))

    assert(len(f.get_stmt().get_stmts()) == 1)

    return f

def test_tc_negate():
    width = 16
    f = build_tc_negate(width);

    sim = Simulator(f)
    sim.set_input("in", bv("16'b0000000000000001"))
    sim.evaluate()
    
    assert(sim.get_output("out") == bv("16'b1111111111111111"))
                  
