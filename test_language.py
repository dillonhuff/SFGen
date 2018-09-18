# from bit_vector import *
# from language import *

# def test_int_type():
#     assert(IntegerType() == IntegerType())

# def build_tc_negate(width):
#     assert(isinstance(width, int))
    
#     f = new_function("tc_negate_" + str(width), Variable("out", ArrayType(width)))
#     f.add_input("in", width)

#     assert(len(f.get_formal_args()) == 1)
    
#     f.add_assign(f.get("out"), ~f.get("in") + const(width, 1))

#     assert(len(f.get_stmt().get_stmts()) == 1)

#     return f

# def build_tc_abs(width):
#     assert(isinstance(width, int))

#     tc_neg = build_tc_negate(width)

#     f = new_function("tc_abs_" + str(width), Variable("out", ArrayType(width)))
#     f.add_input("in", width)

#     is_pos = f.var("is_positive", 1)
#     f.add_assign(is_pos,
#                  eq(f.get("in").bits(width - 1, width - 1), const(1, 0)))

#     f.add_assign(f.get("out"),
#                  case_tf(is_pos,
#                          f.get("in"),
#                          unop(tc_neg, f.get("in"))))

#     return f

# def test_tc_negate():
#     width = 16
#     f = build_tc_negate(width);

#     sim = Simulator(f)
#     sim.set_input("in", bv("16'b0000000000000001"))
#     sim.evaluate()
    
#     assert(sim.get_output("out") == bv("16'b1111111111111111"))

# def test_tc_abs():
#     width = 16
#     f = build_tc_abs(width)

#     sim = Simulator(f)
#     sim.set_input("in", bv("16'b0000000000000001"))
#     sim.evaluate()
    
#     assert(sim.get_output("out") == bv("16'b0000000000000001"))

# # def test_newton_raphson_divide():
# #     width = 16

# #     tc_abs = build_tc_abs(width)

# #     div = new_function("newton_raphson_divide_" + str(width),
# #                        Variable("Q", ArrayType(width)))
# #     div.add_input("N", ArrayType(width))
# #     div.add_input("D", ArrayType(width))

# #     N = div.get("N")    
# #     D = div.get("D")

# #     absN = div.asg(unop(tc_abs, div.get("N")))
# #     absD = div.asg(unop(tc_abs, div.get("D")))

# #     lzc = div.asg(lead_zero_count(absD))
# #     shift_distance = div.asg(lzc - const(width, 1))

# #     N_sgn = div.asg(N[(width - 1):(width - 1)])
# #     D_sgn = div.asg(D[(width - 1):(width - 1)])

# #     #q_tmp = div.asg(absN / absD)

# #     D_ = div.asg(absD << shift_distance)

# #     div.printout('D_ = %b', [D_])
    
# #     one = div.asg(const(width, 1 << (width - 1)))

# #     # Approximate 1 / D_
# #     oneW = div.asg(const(2*width, 1 << (2*width - 1)))
# #     div.printout('oneW = %b', [oneW])

# #     X_tmp = div.asg(oneW / zero_extend(2*width, D_))

# #     div.printout('X_tmp = %b', [X_tmp])

# #     X_norm = div.asg(X_tmp << lead_zero_count(X_tmp))

# #     div.printout('X_norm = %b', [X_norm])

# #     X = X_norm[2*width - width : 2*width - 1]

# #     div.printout('X = %b', [X])
    
# #     widthC = div.asg(const(width, width))
# #     res_shift = div.asg(widthC + (widthC - shift_distance - const(width, 2)))
# #     res_mul = div.asg(zero_extend(2*width, N) * zero_extend(2*width, X))

# #     div.printout('X         = %b', [X])
# #     div.printout('N         = %b', [N])
# #     div.printout('res_mul   = %b', [res_mul])
# #     div.printout('res_shift = %b', [res_shift])

# #     tmp_res = div.asg((res_mul << res_shift)[0:(width - 1)])

# #     div.printout('tmp_res = %b', [tmp_res])

# #     # X = div.asg(one) #div.asg(one / D_)
# #     # X = div.asg(X + fpmul(X, (one - fp_mul(D_, X, width - 1)), width - 1))
# #     # X = div.asg(X + fpmul(X, (one - fp_mul(D_, X, width - 1)), width - 1))
# #     # X = div.asg(X + fpmul(X, (one - fp_mul(D_, X, width - 1)), width - 1))
# #     # X = div.asg(X + fpmul(X, (one - fp_mul(D_, X, width - 1)), width - 1))
# #     # X = div.asg(X + fpmul(X, (one - fp_mul(D_, X, width - 1)), width - 1))    

# #     #tmp_res = div.asg(zero_extend(2*width, N)*zero_extend(2*width, X))
# #     div.add_assign(div.get("Q"),
# #                    case_tf(eq(N_sgn, D_sgn),
# #                            tmp_res,
# #                            -tmp_res))
# #                            # q_tmp,
# #                            # X))
# # #                           X))
# # #                           -q_tmp))

# #     sim = Simulator(div)
# #     sim.set_input("N", bv("16'b10010"))
# #     sim.set_input("D", bv("16'b110"))
# #     sim.evaluate()
# #     assert(sim.get_output("Q") == bv("16'b11"))

# #     sim.set_input("N", bv("16'b10010"))
# #     sim.set_input("D", -bv("16'b110"))
# #     sim.evaluate()
# #     assert(sim.get_output("Q") == -bv("16'b11"))
    
