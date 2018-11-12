# A Python HLS Tool for Writing Special Functions

This repo is a simple synthesis tool that lets you write functional units
like dividers and square roots as python functions using a pre-built bit
vector library and then compile them in to Verilog when you are ready
to synthesize them.

# Getting started

After cloning this repo run the unit tests like so:

```bash
pytest
```

## Example: Cubing a Number

Look in the file [./examples/cube.py](examples/cube.py). You should
see this:

```python
from sfgen.bit_vector import *

def cube(x):
    out = x * x * x
    return out
```

### Synthesizing the Python Function

Now we need to generate verilog for this code. We do this using a synthesis script
located in [examples/synthesize_cube.py](examples/synthesize_cube.py). The code
looks like so:

```python
from sfgen.parser import *
import sfgen.language as l
from sfgen.rtl import *
from sfgen.scheduling import *
from sfgen.utils import *
from sfgen.verilog_backend import *
    
code_gen = codegen_for_module('cube')
f_spec = specialize_types(code_gen, 'cube', [l.ArrayType(32)])

constraints = ScheduleConstraints()
sched = schedule(code_gen, f_spec, constraints)

print(sched.to_string())

mod = generate_rtl(f_spec, sched)

assert(mod.name == f_spec.name)

generate_verilog(mod)
```

To run this script and generate verilog use the command:

```bash
python ./examples/synthesize_cube.py
```

You should now see a new file called cube_32.v that contains an implementation of
the cube function as a combinational circuit using 32 bit multipliers.

```verilog
module builtin_assign_32(in, out);
	input [31:0] in;
	output [31:0] out;

	assign out = in;

endmodule

module builtin_mult_32_32(in1, in0, out);
	input [31:0] in0;
	input [31:0] in1;
	output [31:0] out;

	assign out = in0 * in1;

endmodule

module cube_32(x, out);
	input [31:0] x;
	output [31:0] out;
	wire [31:0] fs_0;
	wire [31:0] fs_1;
	wire [31:0] fresh_wire_0;
	wire [31:0] fresh_wire_2;
	wire [31:0] fresh_wire_4;

	builtin_assign_32 fresh_assign_1(.in(fresh_wire_0), .out(fs_0));
	builtin_mult_32_32 mult_32_0(.in0(x), .in1(x), .out(fresh_wire_0));
	builtin_assign_32 fresh_assign_3(.in(fresh_wire_2), .out(fs_1));
	builtin_mult_32_32 mult_32_1(.in0(fs_0), .in1(x), .out(fresh_wire_2));
	builtin_assign_32 fresh_assign_5(.in(fresh_wire_4), .out(out));
	builtin_assign_32 assign_32_2(.in(fs_1), .out(fresh_wire_4));

endmodule

```

### Adding a Resource Constraint

The implementation of ```cube``` above uses 2 multipliers, but what if we
only want to use one multiplier? We can add a resource constraint that forces
the synthesis program to do both operations on the same multiplier by splitting
the operations up over two cycles.

You can see how to do this in the synthesis script in
[examples/synthesize_cube_one_mult.py](examples/synthesize_cube_one_mult.py).
The script is the same as the previous one with one added line after the creation
of the ```constraints``` variable:

```python
constraints.set_resource_count('mult_32', 1)
```

This line tells the compiler that only one multiplier can be used to implement the
circuit. We run this new synthesis script like so:

```bash
python ./examples/synthesize_cube_one_mult.py
```

The new verilog is a sequential circuit with only one multiplier, and a stage
counter and multiplexers to control the data input to the multiplier:

```verilog
module builtin_counter_1(rst, clk, out);
	input [0:0] clk;
	input [0:0] rst;
	output [0:0] out;

	reg [0:0] stage_num;
	always @(posedge clk) begin
		if (rst) begin
			stage_num <= 0;
		end else if (stage_num == 1) begin
			stage_num <= 0;
		end else begin
			stage_num <= stage_num + 1;
		end
	end
	assign out = stage_num;

endmodule

module builtin_fifo_0_32(in, clk, out);
	input [31:0] in;
	input [0:0] clk;
	output [31:0] out;

	assign out = in;

endmodule

module builtin_fifo_1_32(in, clk, out);
	input [31:0] in;
	input [0:0] clk;
	output [31:0] out;

	reg [31:0] delay_reg_0;
	always @(posedge clk) begin
		delay_reg_0 <= in;
	end
	assign out = delay_reg_0;

endmodule

module builtin_mux_2_32(in1, sel, in0, out);
	input [31:0] in0;
	input [31:0] in1;
	input [0:0] sel;
	output [31:0] out;

	reg [31:0] out_reg;
	always @(*) begin
		case(sel)
			1'b0: out_reg = in0;
			1'b1: out_reg = in1;
		endcase	
	end
	assign out = out_reg;

endmodule

module builtin_assign_32(in, out);
	input [31:0] in;
	output [31:0] out;

	assign out = in;

endmodule

module builtin_mult_32_32(in1, in0, out);
	input [31:0] in0;
	input [31:0] in1;
	output [31:0] out;

	assign out = in0 * in1;

endmodule

module builtin_constant_32_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(out);
	output [31:0] out;

	assign out = 32'bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx;

endmodule

module cube_32(x, en, clk, out);
	input [31:0] x;
	output [31:0] out;
	wire [31:0] fs_0;
	wire [31:0] fs_1;
	wire [0:0] global_stage_counter;
	input [0:0] clk;
	input [0:0] en;
	wire [31:0] fresh_wire_0;
	wire [31:0] fresh_wire_2;
	wire [31:0] fresh_wire_4;
	wire [31:0] fresh_wire_6;
	wire [31:0] fresh_wire_8;
	wire [31:0] fresh_wire_10;
	wire [31:0] fresh_wire_12;
	wire [31:0] undefined_value_16;
	wire [31:0] fresh_wire_17;
	wire [31:0] fresh_wire_19;
	wire [31:0] fresh_wire_21;

	builtin_counter_1 stage_counter(.clk(clk), .rst(en), .out(global_stage_counter));
	builtin_fifo_0_32 fifo_1(.in(x), .out(fresh_wire_0), .clk(clk));
	builtin_fifo_1_32 fifo_3(.in(fs_0), .out(fresh_wire_2), .clk(clk));
	builtin_mux_2_32 in_mux_5(.sel(global_stage_counter), .in0(fresh_wire_0), .in1(fresh_wire_2), .out(fresh_wire_4));
	builtin_fifo_0_32 fifo_7(.in(x), .out(fresh_wire_6), .clk(clk));
	builtin_fifo_1_32 fifo_9(.in(x), .out(fresh_wire_8), .clk(clk));
	builtin_mux_2_32 in_mux_11(.sel(global_stage_counter), .in0(fresh_wire_6), .in1(fresh_wire_8), .out(fresh_wire_10));
	builtin_assign_32 fresh_assign_13(.in(fresh_wire_12), .out(fs_0));
	builtin_assign_32 fresh_assign_14(.in(fresh_wire_12), .out(fs_1));
	builtin_mult_32_32 mult_32_0(.in0(fresh_wire_4), .in1(fresh_wire_10), .out(fresh_wire_12));
	builtin_constant_32_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx x_const_15(.out(undefined_value_16));
	builtin_fifo_0_32 fifo_18(.in(fs_1), .out(fresh_wire_17), .clk(clk));
	builtin_mux_2_32 in_mux_20(.sel(global_stage_counter), .in0(undefined_value_16), .in1(fresh_wire_17), .out(fresh_wire_19));
	builtin_assign_32 fresh_assign_22(.in(fresh_wire_21), .out(out));
	builtin_assign_32 assign_32_1(.in(fresh_wire_19), .out(fresh_wire_21));

endmodule
```

# More Complicated Examples

* [examples/huang_divider.py](examples/huang_divider.py) - A lookup table based Taylor series divider
* [examples/divider.py](examples/divider.py) - A Newton-Raphson divider that uses a lookup table and one iteration of refinement

# The Supported Subset of Python

* Operations on bit vectors from the pre-made bit vector library in
[sfgen/bit_vector](sfgen/bit_vector.py)
* Function calls
* Lookup in pre-computed tables
* Conditional assignment statements

I am working on adding support for structs, if-else statements, and fixed bound loops.

# Dependencies

* Python 3
* pytest