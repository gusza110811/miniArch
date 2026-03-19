from memory import Memory, IO
import termmagic
from execute import Executor, OpcodeFault
from instructions import Instructions
import time

AX, BX, CX, DX, CS, DS, SS, ES, SP, BP = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9

Z, C, N = 0, 1, 2

class Emulator:
    def __init__(self):
        self.io = IO()
        self.executor = Executor(self)

        self.pc = 0 # not accessible from software

        self.registers = [
            0,0,0,0, # ax, bx, cx, dx
            0xf000,0,0,0, # cs, ds, ss, es
            0,0    # sp, bp
        ]

        self.ip = 0

        self.flags = [
            False, # zero
            False, # carry
            False, # negative
        ]

        self.running = True
        self.doTrace = True

        self.trace = []
        self.jumped = False

        self.params = []
    
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
        val = int.from_bytes(tmp,"little",signed=signed)
        self.params.append(val)
        return val

    def main(self,initcode:bytearray):
        self.memory = Memory(initcode)
        doTrace = self.doTrace

        while self.running:
            self.ip = self.pc
            try:
                inst = Instructions(self.fetch())
            except ValueError as e:
                print(self.ip, e)
                self.running == False
            if doTrace:
                self.trace.append((
                    (self.registers[CS],self.ip),
                    self.jumped,
                    inst,
                    self.params,
                    self.registers.copy(),
                    self.flags.copy(),
                    #self.memory.lastAccess() if inst in memAccess else None
                ))
            self.executor.execute(inst)

            self.params = []
    
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

def writeTrace(filename:str, trace:list):
    file = open(filename,"w")
    registerNames = [
        "ax", "bx", "cx", "dx",
        "cs", "ds", "ss", "es",
        "sp", "bp"
    ]
    for item in trace:
        file.write(
            (f"{item[0][0]:04X}:{item[0][1]:04X}" +
            (">" if item[1] else " ") +
            "{0}:{1:02X}".format(str(item[2]),item[3][0] if item[3] else 0).ljust(10) +
            "{0:<5}".format(", ".join([f"{item:4X}" for item in item[3][1:]])) + " " +
            (
                " ".join([f"{registerNames[idx]}={item[4][idx]:04X}" for idx in range(10)])
            ) + " " +
            (
                ('Z' if item[5][0] else "z") +
                ('C' if item[5][1] else "c") +
                ('N' if item[5][2] else 'n')
            ) + " " #+
            #("  " + f"{item[6][0]:05X} = {item[6][1]:X}" if item[6] else "")
            ).rstrip() + "\n"
        )
    file.close()

if __name__ == "__main__":
    termmagic.disable_buffering()
    termmagic.disable_lfcrlf()
    emulator = Emulator()

    trace = True

    emulator.doTrace = trace

    code = open("main.bin","rb").read()

    try:
        emulator.main(code)
    finally:
        time.sleep(0.5)
        termmagic.reset()
    print("")

    emulator.dump()
    if trace:
        writeTrace(".trace",emulator.trace)
