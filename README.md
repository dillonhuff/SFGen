[![Build Status](https://travis-ci.org/dillonhuff/SFGen.svg?branch=master)](https://travis-ci.org/dillonhuff/SFGen)

# A Python3 HLS Tool for Writing Special Functions

This repo is a simple synthesis tool that lets you write functional units
like dividers and square roots as python functions using a pre-built bit
vector library and then compile them in to Verilog when you are ready
to synthesize them.

# Getting started

Run the following commands to install and run the unit tests (note that you will need icarus verilog for some of the unit tests):

```bash
git clone https://github.com/dillonhuff/SFGen.git
cd SFGen
pytest
```

## Example: Cubing a Number

Look in the file [./examples/cube.py](examples/cube.py). You should
see a function ```cube(x)``` that takes in one argument and returns the
cube of the argument:

```python
from sfgen.bit_vector import *

def cube(x):
    out = x * x * x
    return out
```

A simple python testbench for this function is shown in [test/test_cube.py](test/test_cube.py):

```python
from sfgen.bit_vector import *
from examples.cube import *

def test_cube():
    width = 32
    a = bv_from_int(width, 7)
    correct = bv_from_int(width, 7*7*7)

    print('a       =', a)    
    print('correct =', correct)
    print('cube(a) =', cube(a))

    assert(cube(a) == correct)

```

We can run it like so:

```bash
pytest test_main.py test/test_cube.py
```

### Synthesizing the Python Function

With all tests passing we are ready to generate Verilog for our design.
To generate verilog from ```cube``` we use a synthesis script
located in [examples/synthesize_cube.py](examples/synthesize_cube.py). The code
looks like so:

```python
import os
import os.path
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

from sfgen.verilog_backend import *
    
constraints = ScheduleConstraints()
synthesize_verilog('examples/cube', 'cube', [l.ArrayType(32)], constraints)
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
[examples/synthesize_cube_one_mult.py](https://github.com/dillonhuff/SFGen/blob/902742efb62be839dc306b14d5b6ed32ab0d7bf1/examples/synthesize_cube_one_mult.py#L11).
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

## Example: Creating a Pre-Computed Table

Often real functional units like reciprocal dividers or the CORDIC algorithm need
to read from a table of values that is pre-computed at design time. This tool
supports pre-computed tables through a special higher-order function ```lookup_in_table```.

For an example consider the function ```foo``` in [examples/table_lookup.py](examples/table_lookup.py):

```python
from sfgen.bit_vector import *

def table_func(a):
    return a - bv_from_int(a.width(), 1)

def foo(a):
    res = lookup_in_table(a, table_func)

    return res
```

```foo``` calls the ordinary function ```table_func``` which subtracts 1 from its
argument, but instead of calling it directly it calls ```table_func``` on ```a```
through the ```lookup_in_table``` function. This is a cue to the compiler to
pre-compute all possible values of table func and implement it as a table in
verilog.

If we run the synthesis script for ```foo``` using a 4 bit wide argument located in
[examples/synthesize_table_lookup.py](examples/synthesize_table_lookup.py) like so:

```bash
python ./examples/synthesize_table_lookup.py
```

then we get verilog like this:

```verilog
module builtin_assign_4(in, out);
	input [3:0] in;
	output [3:0] out;

	assign out = in;

endmodule

module builtin_table_lookup_table_func_4_4(in, out);
	input [3:0] in;
	output [3:0] out;

	reg [3:0] out_reg;
	always @(*) begin
		case(in)
			4'b0000: out_reg = 4'b1111;
			4'b0001: out_reg = 4'b0000;
			4'b0010: out_reg = 4'b0001;
			4'b0011: out_reg = 4'b0010;
			4'b0100: out_reg = 4'b0011;
			4'b0101: out_reg = 4'b0100;
			4'b0110: out_reg = 4'b0101;
			4'b0111: out_reg = 4'b0110;
			4'b1000: out_reg = 4'b0111;
			4'b1001: out_reg = 4'b1000;
			4'b1010: out_reg = 4'b1001;
			4'b1011: out_reg = 4'b1010;
			4'b1100: out_reg = 4'b1011;
			4'b1101: out_reg = 4'b1100;
			4'b1110: out_reg = 4'b1101;
			4'b1111: out_reg = 4'b1110;
		endcase
	end
	assign out = out_reg;

endmodule

module foo_4(a, res);
	input [3:0] a;
	output [3:0] res;
	wire [3:0] fs_1;
	wire [3:0] fresh_wire_0;
	wire [3:0] fresh_wire_2;

	builtin_assign_4 fresh_assign_1(.in(fresh_wire_0), .out(fs_1));
	builtin_table_lookup_table_func_4_4 builtin_table_lookup_table_func_0(.in(a), .out(fresh_wire_0));
	builtin_assign_4 fresh_assign_3(.in(fresh_wire_2), .out(res));
	builtin_assign_4 assign_4_1(.in(fs_1), .out(fresh_wire_2));

endmodule

```

The ```table_function``` has been pre-compiled in to a giant case statement that
can be synthesized as an SRAM. Be warned that large tables may take a long time
to calculate!

# More Complicated Examples

* [examples/huang_divider.py](examples/huang_divider.py) - A lookup table based Taylor series divider for signed integers.
* [examples/divider.py](examples/divider.py) - A Newton-Raphson divider for signed integers that uses a lookup table and one iteration of refinement.

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
* Icarus Verilog for the unit test suite