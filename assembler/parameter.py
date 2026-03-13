class BaseParameter:
    def __init__(self, value: int, length=2):
        self.value = value
        self.length= length
        "bytes, in powers of twos"
    
    def get(self,size:int):
        raise NotImplementedError(f"get() is not implemented for {self.__class__.__name__}")

class Immediate(BaseParameter):
    def __repr__(self):
        return f"ImmediateParameter(self.value)"
    
    def get(self,size=2,signed=False):
        if size == 0:
            return self.value.to_bytes((max(self.value.bit_length(),1)+7)//8, byteorder='little', signed=signed)
        else:
            return self.value.to_bytes(size, byteorder='little', signed=signed)

class Register(BaseParameter):
    def __init__(self, value, length=2):
        super().__init__(value, length)
    def __repr__(self):
        return f"RegisterParameter({self.value})"

class Dereference(BaseParameter):
    def __init__(self, value:int, length:int, base:int):
        super().__init__(value)
        self.length = length
        self.base = base
    def __repr__(self):
        return f"DereferenceParameter({self.value})"
    def get(self,size=2):
        return self.value.to_bytes(size, byteorder='little')

class IndirectDereference(BaseParameter):
    def __init__(self, value, length):
        super().__init__(value)
        self.length = length
    def __repr__(self):
        return f"IndirectDereferenceParameter(*{self.base}  {self.length})"
