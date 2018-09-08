import bit_vector as b

def tc_neg(bv):
    return ~bv + b.bv_from_int(bv.width(), 1)

print('tc_neg 1 =', tc_neg(b.bv_from_int(16, 1)))
