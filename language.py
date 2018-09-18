class Type:
    def __init__(self):
        return None

class IntegerType(Type):
    def __init__(self):
        Type.__init__(self)

    def __eq__(self, other):
        return isinstance(other, IntegerType)

    def to_string(self):
        return 'Z'

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

class FunctionType(Type):
    def __init__(self, arg_types, out_type):
        Type.__init__(self)
        self.arg_types = arg_types
        self.out_type = out_type

    def __eq__(self, other):
        if (not isinstance(other, ArrayType)):
            return False
        if self.out_type != other.out_type:
            return False

        if len(self.arg_types) != len(other.arg_types):
            return False

        for i in range(len(self.arg_types)):
            if self.arg_types[i] != other.arg_types[i]:
                return False
        return True

    def to_string(self):
        s = ''
        s += comma_list(list(map(lambda n : n.to_string(), self.arg_types)))
        s += ' -> ' + self.out_type.to_string()
        return '[' + str(self.w) + ']'

class ArrayType(Type):
    def __init__(self, w):
        Type.__init__(self)
        self.w = w

    def __eq__(self, other):
        if (not isinstance(other, ArrayType)):
            return False
        return self.w == other.w

    def width(self):
        return self.w

    def to_string(self):
        return '[' + str(self.w) + ']'

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()
