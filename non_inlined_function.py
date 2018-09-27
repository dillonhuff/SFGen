def plus_nums(a, b):
    return a + b

def non_inlined(x):
    out = plus_nums(plus_nums(x, x), x)
    return out
