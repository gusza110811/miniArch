from memory import Memory, IO
import termmagic
from execute import Executor, OpcodeFault
import time
from instructions import Instructions

AX, BX, CX, DX, CS, DS, SS, ES, IP, SP, BP = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

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

        self.running = True
    
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
            inst = Instructions(self.fetch())
            variant = self.fetch()

            self.executor.execute(inst,variant)
    
    def dump(self):
        names = ["ax","bx","cx","dx",
                 "cs","ds","ss","es",
                 "ip","sp","bp"]
        
        for idx,val in enumerate(self.registers):
            print(f"{names[idx]}: {val}")


if __name__ == "__main__":
    termmagic.disable_buffering()
    emulator = Emulator()

    code = open("main.bin","rb").read()

    try:
        emulator.main(code)
    finally:
        termmagic.reset()
    
    emulator.dump()
