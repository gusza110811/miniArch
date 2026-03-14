from typing import TYPE_CHECKING
from instructions import Instructions as insts

AX, BX, CX, DX, CS, DS, SS, ES, IP, SP, BP = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

class OpcodeFault(Exception):pass

class Executor:
    def __init__(self, emulator:"Emulator"):
        self.emulator = emulator
    def execute(self, inst:insts, instvariant:int):
        emulator = self.emulator
        fetchs = self.emulator.fetchs
        memory = emulator.memory
        io = emulator.io
        get = emulator.get
        set = emulator.set
        instnovariant = [insts.halt]

        # instruction variants (for those that supports it)
        # bits 0-3: source
        # bits 4-7: dest
        # source and dest as direct value:
        # 0: ax, bx, cx, dx
        # 4: cs, ds, ss, es
        # 8: ip, sp, bp
        # source and dest as dereference:
        # 0: cs+bx, ds+bx, ss+bx, es+bx
        # 4: ip+bx, sp+bx, bp+bx, (unused)
        # 8: cs+imm, ds+imm, ss+imm, es+imm
        # B: ip+imm, sp+imm, bp+imm
        if not inst in instnovariant:
            source = instvariant & 0xF
            dest = instvariant >> 4

        match inst:
            case insts.rmov:
                set(dest,get(source))

            case insts.ldi4:
                set(dest,source)
            case insts.ldi8:
                set(dest,fetchs(1))
            case insts.ldi16:
                set(dest,fetchs(2))
            
            case insts.ldb:
                if source < 8:
                    srcval = memory.loadb(get(source+4)+get(1))
                elif source <= 13:
                    addr = (get(source-4)<<4)+fetchs(2)
                    srcval = memory.loadb(addr)
                else: raise OpcodeFault
                set(dest,srcval)
            case insts.ldw:
                if source < 8:
                    addr = (get(source+4)<<4)+get(1)
                    srcval = memory.loadw(addr)
                elif source <= 13:
                    addr = (get(source-4)<<4)+fetchs(2)
                    srcval = memory.loadw(addr)
                else: raise OpcodeFault
                set(dest,srcval)
            case insts.stb:
                if dest < 8:
                    addr = (get(source+4)<<4)+get(1)
                elif dest <= 13:
                    addr = (get(dest-4)<<4)+fetchs(2)
                memory.storeb(addr,get(source))
            case insts.stw:
                if dest < 8:
                    addr = get(dest+4)+get(1)
                elif dest <= 13:
                    addr = (get(dest-4)<<4)+fetchs(2)
                memory.storew(addr,get(source))

            case insts.halt:
                emulator.running = False

if TYPE_CHECKING: from main import Emulator
