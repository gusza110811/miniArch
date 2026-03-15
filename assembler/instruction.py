from parameter import *

class Err:
    def __init__(self,
            msg:str,
            pos:int,
            hint:str="",):
        self.msg = msg
        self.pos = pos
        self.hint = hint

        if msg == "not implemented":
            self.hint += "\ncome back to writing the assembler you donkey"

map = {}

def register(name:str,cls:"Instruction"):
    map[name] = cls

class Instruction:
    def __init__(self,args:list[BaseParameter]):
        self.args = args
    def __repr__(self):
        return f"{self.__class__.__name__}(args={self.args})"
    def get(self, pc:int, size=2) -> bytes|Err:
        raise NotImplementedError(f"get() not implemented for {self.__class__.__name__}")

    @classmethod
    def from_str(cls, name:str, args:list[BaseParameter]) -> "Instruction":
        if name not in map:
            raise SyntaxError(f"unknown instruction '{name}'")
        return map[name](args)
    
    def check_type(self, index:int, expect:BaseParameter|list[BaseParameter]):
        if not isinstance(expect,list):
            if isinstance(self.args[index],expect):
                return True
            else:
                return False
        else:
            for exp in expect:
                if isinstance(self.args[index],exp):
                    return True
            return False
    def check_count(self, expect:int):
        if expect == len(self.args):
            return 0
        if expect > len(self.args):
            return 1
        if expect < len(self.args):
            return -1

class Mov(Instruction):
    def get(self, pc, size=2):
        dest = self.args[0]
        src = self.args[1]
        destval = dest.value
        srcval = src.value
        destT = dest.__class__
        srcT = src.__class__

        srcL = src.length
        destL = dest.length
        length = None

        datalen = list("bwdq")

        if srcL != None and destL != None and srcL != destL and srcT != Register and destT != Register:
            return Err("conflicting data length",0,f"{datalen.index(destL)} vs {datalen.index(srcL)}")

        length = destL or srcL

        if length is None:
            if destT == Register:
                length = dest.default_size
            elif srcT == Register:
                length = src.default_size

        if length is None:
            return Err("ambiguous data length",0)

        out = bytearray()

        if destT == Immediate:
            return Err("unsupported operand",0,"cannot save to immediate value")

        if destT == Register:
            if srcT == Register:
                out.append(0x10)
                out.append((destval<<4)|srcval)
            elif srcT == Immediate:
                out.append(0x11)
                if srcval > 15:
                    return Err("Immediate value too large",1,f"{src.value} does not fit in 4 bit, try using `ldi8` or `ldi`")
                out.append((destval<<4)|srcval)
            elif srcT == Dereference:
                if length == 0:
                    out.append(0x19)
                else:
                    out.append(0x1B)
                base = src.base
                offset = src.value
                target = dest.value
                descriptor = (target << 4) | (base+8)
                out.append(descriptor)
                out.extend(offset.to_bytes(2,'little',signed=True))
            elif srcT == IndirectDereference:
                base = src.value
                if length == 0:
                    out.append(0x19)
                else:
                    out.append(0x1B)
                target = dest.value
                descriptor = (target << 4) | base
                out.append(descriptor)

        elif destT == Dereference:
            if srcT == Register:
                if length == 0:
                    out.append(0x18)
                else:
                    out.append(0x1A)
                base = dest.base
                offset = dest.value
                source = src.value
                descriptor = ((base+8) << 4)|source
                out.append(descriptor)
                out.extend(offset.to_bytes(2,'little',signed=True))
            elif srcT == Dereference or srcT == IndirectDereference:
                return Err("unsupported operand",1,"copy directly from memory to memory")
            elif srcT == Immediate:
                return Err("unsupported operand",1,"cannot store immediate value directly to memory")
        elif destT == IndirectDereference:
            if srcT == Register:
                base = dest.value
                if length == 0:
                    out.append(0x18)
                else:
                    out.append(0x1A)
                source = src.value
                descriptor = (base << 4) | source
                out.append(descriptor)
            elif srcT == Dereference or srcT == IndirectDereference:
                return Err("unsupported operand",1,"cannot copy directly from memory to memory")
            elif srcT == Immediate:
                return Err("unsupported operand",1,"cannot store immediate value directly to memory")

        if out:
            return bytes(out)
        
        return Err("not implemented",0,f"{destT} and {srcT} pair is not implemented")
register("mov",Mov)
class Ldi8(Instruction):
    def get(self, pc, size=2):
        countcmp = self.check_count(2)
        if countcmp:
            return Err(("not enough" if countcmp == -1 else "too many") + " parameter",-1,f"expected 2, got {len(self.args)}")
        dest = self.args[0]
        src = self.args[1]
        destval = dest.value
        srcval = src.value

        if not self.check_type(0,Register):
            return Err("unsupported operand",0,f"Expected a Register, not {dest.__class__.__name__}")
        if not self.check_type(1,Immediate):
            return Err("unsupported operand",1,f"Expected an Immediate, not {src.__class__.__name__}")
        
        if srcval > 255:
            return Err("immediate value too large",1,f"{srcval} does not fit in 8 bits")

        return bytes([
            0x12, destval << 4, srcval
        ])
register("ldi8",Ldi8)
class Ldi(Instruction):
    def get(self, pc, size=2):
        countcmp = self.check_count(2)
        if countcmp:
            return Err(("not enough" if countcmp == -1 else "too many") + " parameter",-1,f"expected 2, got {len(self.args)}")
        dest = self.args[0]
        src = self.args[1]
        destval = dest.value
        srcval = src.value

        if not self.check_type(0,Register):
            return Err("unsupported operand",0,f"Expected a Register, not {dest.__class__.__name__}")
        if not self.check_type(1,Immediate):
            return Err("unsupported operand",1,f"Expected an Immediate, not {src.__class__.__name__}")
        
        if srcval > 0xFFFF:
            return Err("immediate value too large",1,f"{srcval} does not fit in 16 bit")

        return bytes([
            0x13, (destval << 4)
        ]) + src.get(2)
register("ldi",Ldi)

class Add(Instruction):
    def get(self, pc, size=2):
        countcmp = self.check_count(2)
        if countcmp:
            return Err(("not enough" if countcmp == -1 else "too many") + " parameter",-1,f"expected 2, got {len(self.args)}")
        dest = self.args[0]
        src = self.args[1]
        destval = dest.value
        srcval = src.value
        destT = dest.__class__
        srcT = src.__class__

        out = bytearray()

        if destT == Immediate:
            return Err("unsupported operand",0,"cannot add to immediate value")
        if destT == Dereference or destT == IndirectDereference:
            return Err("unsupported operand",0,"cannot add directly to memory")
        if srcT == Dereference or srcT == IndirectDereference:
            return Err("unsupported operand",0,"cannot add directly from memory")
        
        dest:Register
        if srcT == Register:
            out.append(0x20)
            out.append((destval<<4) | (srcval))
        elif srcT == Immediate:
            if srcval > 15:
                return Err("Immediate value too large",1,f"{src.value} does not fit in 4 bit, try using `addi8` or `addi`")
            out.append(0x21)
            out.append((destval<<4) | (srcval))
        
        return bytes(out)
register("add",Add)
class Addi8(Instruction):
    def get(self, pc, size=2):
        countcmp = self.check_count(2)
        if countcmp:
            return Err(("not enough" if countcmp == -1 else "too many") + " parameter",-1,f"expected 2, got {len(self.args)}")
        dest = self.args[0]
        src = self.args[1]
        if not self.check_type(0,Register):
            return Err("unsupported operand",0,f"cannot add immediate value to {dest.__class__.__name__}")
        if not self.check_type(1,Immediate):
            return Err("unsupported operand",1,f"add immediate needs immediate value, not {dest.__class__.__name__}")
        
        destval = dest.value
        srcval = src.value
        return bytes([
            0x21,destval<<4,srcval
        ])
register("addi8",Addi8)
class Addi(Instruction):
    def get(self, pc, size=2):
        countcmp = self.check_count(2)
        if countcmp:
            return Err(("not enough" if countcmp == -1 else "too many") + " parameter",-1,f"expected 2, got {len(self.args)}")
        dest = self.args[0]
        src = self.args[1]
        if not self.check_type(0,Register):
            return Err("unsupported operand",0,f"cannot add immediate value to {dest.__class__.__name__}")
        if not self.check_type(1,Immediate):
            return Err("unsupported operand",1,f"add immediate needs immediate value, not {dest.__class__.__name__}")
        destval = dest.value
        srcval = src.value
        if srcval > 0xFFFF:
            return Err("immediate value too large",1,f"{srcval} does not fit in 16 bit")
        return bytes([
            0x22,destval<<4
        ]) + src.get(2)
register("addi",Addi)

class Sub(Instruction):
    def get(self, pc, size=2):
        countcmp = self.check_count(2)
        if countcmp:
            return Err(("not enough" if countcmp == -1 else "too many") + " parameter",-1,f"expected 2, got {len(self.args)}")
        dest = self.args[0]
        src = self.args[1]
        destval = dest.value
        srcval = src.value
        destT = dest.__class__
        srcT = src.__class__

        out = bytearray()

        if destT == Immediate:
            return Err("unsupported operand",0,"cannot add to immediate value")
        if destT == Dereference or destT == IndirectDereference:
            return Err("unsupported operand",0,"cannot add directly to memory")
        if srcT == Dereference or srcT == IndirectDereference:
            return Err("unsupported operand",0,"cannot add directly from memory")
        
        dest:Register
        if srcT == Register:
            out.append(0x24)
            out.append((destval<<4) | (srcval))
        elif srcT == Immediate:
            if srcval > 15:
                return Err("Immediate value too large",1,f"{src.value} does not fit in 4 bit, try using `addi8` or `addi`")
            out.append(0x25)
            out.append((destval<<4) | (srcval))
        
        return bytes(out)
register("sub",Sub)
class Subi8(Instruction):
    def get(self, pc, size=2):
        countcmp = self.check_count(2)
        if countcmp:
            return Err(("not enough" if countcmp == -1 else "too many") + " parameter",-1,f"expected 2, got {len(self.args)}")
        dest = self.args[0]
        src = self.args[1]
        if not self.check_type(0,Register):
            return Err("unsupported operand",0,f"cannot add immediate value to {dest.__class__.__name__}")
        if not self.check_type(1,Immediate):
            return Err("unsupported operand",1,f"add immediate needs immediate value, not {dest.__class__.__name__}")
        
        destval = dest.value
        srcval = src.value
        return bytes([
            0x26,destval<<4,srcval
        ])
register("subi8",Subi8)
class Subi(Instruction):
    def get(self, pc, size=2):
        countcmp = self.check_count(2)
        if countcmp:
            return Err(("not enough" if countcmp == -1 else "too many") + " parameter",-1,f"expected 2, got {len(self.args)}")
        dest = self.args[0]
        src = self.args[1]
        if not self.check_type(0,Register):
            return Err("unsupported operand",0,f"cannot add immediate value to {dest.__class__.__name__}")
        if not self.check_type(1,Immediate):
            return Err("unsupported operand",1,f"add immediate needs immediate value, not {dest.__class__.__name__}")
        destval = dest.value
        srcval = src.value
        if srcval > 0xFFFF:
            return Err("immediate value too large",1,f"{srcval} does not fit in 16 bit")
        return bytes([
            0x27,destval<<4
        ]) + src.get(2)
register("subi",Subi)

class Halt(Instruction):
    def get(self, pc, size=2):
        if self.check_count(0):
            return Err("too many parameter",0,"`halt` does not take any parameter")
        return b"\xff"
register("halt",Halt)
