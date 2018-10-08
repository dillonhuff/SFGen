class Complex:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

def add_complex(a, b):
    return Complex(a.real + b.real, a.imag + b.imag)
