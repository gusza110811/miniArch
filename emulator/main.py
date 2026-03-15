from memory import Memory, IO
import termmagic
from execute import Executor, OpcodeFault
from instructions import Instructions

AX, BX, CX, DX, CS, DS, SS, ES, IP, SP, BP = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

Z, C, N = 0, 1, 2

class Emulator:
    def __init__(self):
        self.io = IO()
        self.executor = Executor(self)

        self.pc = 0 # not accessible from software

        self.registers = [
            0,0,0,0, # ax, bx, cx, dx
            0xf000,0,0,0, # cs, ds, ss, es
            0,0,0    # ip, sp, bp
        ]

        self.flags = [
            False, # zero
            False, # carry
            False  # negative
        ]

        self.running = True
    
    def check(self,reg:int):
        res = self.registers[reg]
        if res == 0:
            self.flags[Z] = True
        else:
            self.flags[Z] = False
        if res > 0xFFFF:
            self.flags[C] = True
            self.registers[reg] &= 0xFFFF
        else:
            self.flags[C] = False
        if res < 0:
            self.flags[N] = True
            self.registers[reg] &= 0xFFFF
        else:
            self.flags[N] = False
    
    def get(self,id:int) -> int:
        if id >= len(self.registers):
            raise OpcodeFault
        return self.registers[id]
    def set(self,reg:int,val:int):
        self.registers[reg] = val
    
    def fetch(self):
        val = self.memory.loadb((self.registers[CS] << 4) + self.pc)
        self.pc += 1
        return val
    
    def fetchs(self, count:int, signed=False):
        tmp = bytearray()
        for idx in range(count):
            tmp.append(self.fetch())
        return int.from_bytes(tmp,"little",signed=signed)
    
    def main(self,initcode:bytearray):
        self.memory = Memory(initcode)

        while self.running:
            self.registers[IP] = self.pc
            try:
                inst = Instructions(self.fetch())
            except ValueError as e:
                print(self.registers[IP], e)
                self.running == False

            self.executor.execute(inst)
    
    def dump(self):
        names = ["ax","bx","cx","dx",
                 "cs","ds","ss","es",
                 "ip","sp","bp"]
        
        for idx,val in enumerate(self.registers):
            print(f"{names[idx]}: {val:4x}")

        itemperline = 8
        items = 0
        
        print("\nRam:")
        
        for val in self.truncate_memory(self.memory.ram):
            print(val,end="  ")
            items += 1
            if items == itemperline:
                print()
                items = 0
        items = 0
        print("\nRom:")
        for val in self.truncate_memory(self.memory.rom):
            print(val,end="  ")
            items += 1
            if items == itemperline:
                print()
                items = 0
        print()

    def truncate_memory(self, mem, start: int = 0, end: int = None):
        result = []
        if end is None:
            end = len(mem.values)

        prev_value = None
        repeat_count = 0
        printed = False

        for i in range(start, end):
            value = mem.values[i]

            if value == prev_value:
                repeat_count += 1
                printed = False
            else:
                if repeat_count > 0:
                    if not printed:
                        if repeat_count > 1:
                            result.append(f"... {repeat_count} times")
                        else:
                            result.append("... repeated")
                        printed = True
                    repeat_count = 0

                result.append(f"{i:05X}: x{value:02X}")
                prev_value = value

        if repeat_count > 0:
            result.append(f"    ... repeated to {(end):04X}")
        
        return result


if __name__ == "__main__":
    termmagic.disable_buffering()
    emulator = Emulator()

    code = open("main.bin","rb").read()

    try:
        emulator.main(code)
    finally:
        termmagic.reset()
    
    emulator.dump()
