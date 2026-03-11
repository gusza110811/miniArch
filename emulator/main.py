from memory import Ram, IO
import termmagic
from execute import Executor
import time
from instructions import Instructions

AX, BX, CX, DX, CS, DS, SS, ES, IP, SP, BP = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

class Emulator:
    def __init__(self):
        self.ram = Ram()
        self.io = IO()
        self.executor = Executor(self)

        self.pc = 0 # not accessible from software

        self.registers = [
            0,0,0,0, # ax, bx, cx, dx
            0,0,0,0, # cs, ds, ss, es
            0,0,0    # ip, sp, bp
        ]

        self.running = True
    
    def get(self,id:int,signed=False) -> int:
        if id == 11:
            return self.fetchs(2,signed)
        else:
            return self.registers[id]
    def set(self,reg:int,val:int):
        self.registers[reg] = val
    
    def fetch(self):
        val = self.ram.load((self.registers[CS] << 4) + self.pc)
        self.pc += 1
        return val
    
    def fetchs(self, count:int, signed=False):
        tmp = bytearray()
        for idx in range(count):
            tmp.append(self.fetch())
        return int.from_bytes(tmp,"little",signed=signed)
    
    def main(self,initcode:bytearray,initcodepos=0):
        for idx, byte in enumerate(initcode):
            self.ram.store(initcodepos+idx,byte)

        while self.running:
            self.registers[IP] = self.pc
            inst = Instructions(self.fetch())
            variant = self.fetch()

            print(f"{self.registers[IP]}: {inst}")

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

    testCode = bytearray([
        0x13, 0x0B, 0x01, 0x00,
        0x13, 0x10,
        0xff, 0x00
    ])

    try:
        emulator.main(testCode)
    finally:
        termmagic.reset()
    
    emulator.dump()
