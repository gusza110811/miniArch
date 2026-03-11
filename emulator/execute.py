from typing import TYPE_CHECKING
from instructions import Instructions as insts

AX, BX, CX, DX, CS, DS, SS, ES, IP, SP, BP = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

class OpcodeFault(Exception):pass

class Executor:
    def __init__(self, emulator:"Emulator"):
        self.emulator = emulator
    def execute(self, inst:insts, instvariant:int):
        emulator = self.emulator
        ram = emulator.ram
        io = emulator.io
        get = emulator.get
        set = emulator.set

        # instruction variants (for those that supports it)
        # bits 0-3: source
        # bits 4-7: dest
        # source and dest as values:
        # 0: ax, bx, cx, dx
        # 4: cs, ds, ss, es
        # 8: ip, sp, bp, imm
        # source and dest as address:
        # 0: ds+ax, ds+bx, ds+cx, ds+dx
        # 4: cs+imm, ds+imm, ss+imm, es+imm
        # 8: ip+imm, sp+imm, bp+imm, imm
        source = instvariant & 0xF
        dest = instvariant >> 4
        if 0 >= source > 11:
            raise OpcodeFault
        if 0 >= dest > 10:
            raise OpcodeFault

        match inst:
            case insts.rmov:
                set(dest,get(source,True))
            
            case insts.halt:
                emulator.running = False

if TYPE_CHECKING: from main import Emulator
