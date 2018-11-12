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

```python
from sfgen.bit_vector import *

def cube(x):
    out = x * x * x
    return out

```

### Synthesizing the Python Function

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

```python
constraints.set_resource_count('mult_32', 1)
```

```bash
python ./examples/synthesize_cube.py
```

# More Complicated Examples

* examples/huang_divider.py - A lookup table based Taylor series divider
* examples/divider.py - A Newton-Raphson divider that uses a lookup table and one iteration of refinement

# Dependencies

* Python 3
* pytest