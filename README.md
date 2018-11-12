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

```bash
python ./examples/synthesize_cube.py
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
python ./examples/synthesize_cube.py
```

# More Complicated Examples

* [examples/huang_divider.py](examples/huang_divider.py) - A lookup table based Taylor series divider
* [examples/divider.py](examples/divider.py) - A Newton-Raphson divider that uses a lookup table and one iteration of refinement

# Dependencies

* Python 3
* pytest