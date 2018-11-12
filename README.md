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

To see an example of synthesis run:

```bash
python synthesize_cube.py
```

# Dependencies

* Python 3
* pytest