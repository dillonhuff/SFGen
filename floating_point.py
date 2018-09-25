def float_multiply(a, b, exp_start, exp_end, mant_start, mant_end):
    assert(a.width() == b.width())
    assert((exp_end - exp_start + 1) + (mant_end - mant_start + 1) + 1 == a.width())
    out = a
    return a
