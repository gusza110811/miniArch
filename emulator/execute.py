from typing import TYPE_CHECKING
from instructions import Instructions as insts

AX, BX, CX, DX, CS, DS, SS, ES, SP, BP = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9

class OpcodeFault(Exception):pass

class Executor:
    def __init__(self, emulator:"Emulator"):
        self.emulator = emulator
    def execute(self, inst:insts):
        emulator = self.emulator
        fetchs = self.emulator.fetchs
        memory = emulator.memory
        io = emulator.io
        get = emulator.get
        set = emulator.set
        check = emulator.check
        instnovariant = [insts.halt]
        instcheck = [
            insts.add,insts.addi4,insts.addi8,insts.addi,
            insts.sub,insts.subi4,insts.subi8,insts.subi
        ]

        # instruction variants (for those that supports it)
        # bits 0-3: source
        # bits 4-7: dest
        # source and dest as direct value:
        # 0: ax, bx, cx, dx
        # 4: cs, ds, ss, es
        # 8: sp, bp
        # source and dest as dereference:
        # 0: cs+bx, ds+bx, ss+bx, es+bx
        # 4: ip+bx, sp+bx, bp+bx, (unused)
        # 8: cs+imm, ds+imm, ss+imm, es+imm
        # B: sp+imm, bp+imm
        dest, source = None, None
        if not inst in instnovariant:
            instvariant = fetchs(1)
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
                    if dest < 8:
                        addr = (get(source+4)<<4)+get(1)
                    elif dest <= 13:
                        addr = (get(dest-4)<<4)+fetchs(2)
                    srcval = memory.loadb(addr)
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

            case insts.add:
                set(dest,get(dest)+get(source))
            case insts.addi4:
                set(dest,get(dest)+source)
            case insts.addi8:
                set(dest,get(dest)+fetchs(1))
            case insts.addi:
                set(dest,get(dest)+fetchs(2))
            case insts.sub:
                set(dest,get(dest)-get(source))
            case insts.subi4:
                set(dest,get(dest)-source)
            case insts.subi8:
                set(dest,get(dest)-fetchs(1))
            case insts.subi:
                set(dest,get(dest)-fetchs(2))

            case insts.halt:
                emulator.running = False
        if inst in instcheck:
            check(dest)

if TYPE_CHECKING: from main import Emulator
