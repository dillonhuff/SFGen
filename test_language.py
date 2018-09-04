from bit_vector import *
from language import *

def test_tc_negate():
    width = 16
    f = new_function("f", Variable("out", ArrayType(width)))
    f.add_input("in", width)

    f.stmt().add_assign(f.get("out"), ~f.get("in") + const(width, 1))

    sim = Simulator(f)
    sim.set_input("in", bv("16'b0000000000000001"))
    sim.evaluate()
    
    assert(sim.get_output("out") == bv("16'b1111111111111111"))
                  
