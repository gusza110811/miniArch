from typing import TYPE_CHECKING
from instructions import Instructions as insts

AX, BX, CX, DX, CS, DS, SS, ES, SP, BP,   AH, BH, CH, DH = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,   12, 13, 14, 15
Z, C, N, O, I = 0, 1, 2, 3, 4

class OpcodeFault(Exception):pass

class Executor:
    def __init__(self, emulator:"Emulator"):
        self.emulator = emulator
    def execute(self, inst:insts):
        emulator = self.emulator
        pushb = self.emulator.pushb
        pushw = self.emulator.pushw
        popb = self.emulator.popb
        popw = self.emulator.popw
        fetchs = self.emulator.fetchs
        memory = emulator.memory
        io = emulator.io
        get = emulator.get
        set = emulator.set
        flags = emulator.flags
        ip = emulator.ip
        check = emulator.check
        instnovariant = [
            insts.halt, insts.nop0, insts.nop1,
            insts.ret,
            insts.jmpf, insts.callf, insts.retf,
            insts.pushf, insts.popf, insts.pusha, insts.popa,
        ]
        instcheck = [
            insts.add,insts.addi4,insts.addi8,insts.addi, insts.neg_,
            insts.sub,insts.subi4,insts.subi8,insts.subi,
        ]

        # instruction variants (for those that supports it)
        # bits 0-3: source
        # bits 4-7: dest
        # source and dest as direct value:
        # 0: ax, bx, cx, dx
        # 4: cs, ds, ss, es
        # 8: sp, bp
        # C: ah, bh, ch, dh
        # source and dest as dereference:
        # 0: cs+bx, ds+bx, ss+bx, es+bx
        # 4: ip+bx, sp+bx, bp+bx, (unused)
        # 8: cs+imm, ds+imm, ss+imm, es+imm
        # C: sp+imm, bp+imm
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
                        seg = get(source+4)
                        addr = get(BX)
                    elif dest <= 13:
                        seg =get(dest-4)
                        addr = fetchs(2)
                    srcval = memory.loadb(seg,addr)
                elif source <= 13:
                    seg = get(source-4)
                    addr = fetchs(2)
                    srcval = memory.loadb(seg,addr)
                else: raise OpcodeFault
                set(dest,srcval)
            case insts.ldw:
                if source < 8:
                    seg = get(source+4)
                    addr = get(BX)
                    srcval = memory.loadw(seg,addr)
                elif source <= 13:
                    seg = get(source-4)
                    addr = fetchs(2)
                    srcval = memory.loadw(seg,addr)
                else: raise OpcodeFault
                set(dest,srcval)
            case insts.stb:
                if dest < 8:
                    seg = get(dest+4)
                    addr = get(1)
                elif dest <= 13:
                    seg = get(dest-4)
                    addr = fetchs(2)
                memory.storeb(seg,addr,get(source))
            case insts.stw:
                if dest < 8:
                    seg = get(dest+4)
                    addr = get(1)
                elif dest <= 13:
                    seg = get(dest-4)
                    addr = fetchs(2)
                memory.storew(seg,addr,get(source))

            case insts.out:
                value = get(source)
                io.write(get(dest),value)
            
            case insts.inp:
                value = io.read(get(source))
                set(dest,value)

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
            case insts.cmp:
                prev = get(dest)
                set(dest,prev-get(source))
                check(dest)
                set(dest,prev)
            case insts.cmpi4:
                prev = get(dest)
                set(dest,prev-source)
                check(dest)
                set(dest,prev)
            case insts.cmpi8:
                prev = get(dest)
                set(dest,prev-fetchs(1))
                check(dest)
                set(dest,prev)
            case insts.cmpi:
                prev = get(dest)
                set(dest,prev-fetchs(2))
                check(dest)
                set(dest,prev)
            case insts.neg_:
                set(dest,-get(dest))
            case insts.sxtbw:
                value = get(dest)
                if value & 0x80:
                    set(dest,value|0xFF00)
                else:
                    set(dest,value&0x00FF)

            case insts.and_:
                set(dest,get(dest)&get(source))
            case insts.andi:
                set(dest,get(dest)&fetchs(2))
            case insts.or_:
                set(dest,get(dest)|get(source))
            case insts.ori:
                set(dest,get(dest)|fetchs(2))
            case insts.xor_:
                set(dest,get(dest)^get(source))
            case insts.xori:
                set(dest,get(dest)^fetchs(2))
            case insts.shr:
                set(dest,get(dest)>>get(source))
            case insts.shri4:
                set(dest,get(dest)>>source)
            case insts.shl:
                set(dest,(get(dest)<<get(source)))
            case insts.shli4:
                set(dest,(get(dest)<<source))
            case insts.not_:
                set(dest,~get(dest)&0xFFFF)

            case insts.jmp:
                cond = source
                distance = dest
                address = None
                match distance:
                    case 0:
                        address = ip + fetchs(1,True)
                    case 1:
                        address = ip + fetchs(2,True)
                    case 2:
                        address = fetchs(2)
                match cond:
                    case 0:
                        if not flags[Z]:
                            return
                    case 1:
                        if flags[Z]:
                            return
                    case 2:
                        if not flags[C]:
                            return
                    case 3:
                        if flags[C]:
                            return
                    case 4:
                        if not flags[N]:
                            return
                    case 5:
                        if flags[N]:
                            return
                    case 16:
                        pass

                emulator.pc = address
            case insts.call:
                cond = source
                distance = dest
                address = None
                match distance:
                    case 0:
                        address = ip + fetchs(1,True)
                    case 1:
                        address = ip + fetchs(2,True)
                    case 2:
                        address = fetchs(2)
                match cond:
                    case 0:
                        if not flags[Z]:
                            return
                    case 1:
                        if flags[Z]:
                            return
                    case 2:
                        if not flags[C]:
                            return
                    case 3:
                        if flags[C]:
                            return
                    case 4:
                        if not flags[N]:
                            return
                    case 5:
                        if flags[N]:
                            return
                    case 16:
                        pass

                pushw(emulator.pc)
                emulator.pc = address
            case insts.ret:
                addr = popw()
                emulator.pc = addr

            case insts.jmpf:
                seg = fetchs(2)
                target = fetchs(2)

                set(CS,seg)
                emulator.pc = target
            case insts.callf:
                pushw(get(CS))
                pushw(emulator.pc)
                seg = fetchs(2)
                target = fetchs(2)

                set(CS,seg)
                emulator.pc = target
            case insts.retf:
                emulator.pc = popw()
                set(CS,popw())

            case insts.pushb:
                pushb(get(source))
            case insts.pushw:
                pushw(get(source))
            case insts.popb:
                set(dest,popb())
            case insts.popw:
                set(dest,popw())
            case insts.pushf:
                # push all flags as a byte
                flagsbyte = 0
                for i in range(8):
                    flagsbyte |= (flags[i] << i)
                pushb(flagsbyte)
            case insts.popf:
                flagsbyte = popb()
                for i in range(8):
                    flags[i] = (flagsbyte >> i) & 1
            case insts.pusha:
                pushw(get(AX))
                pushw(get(BX))
                pushw(get(CX))
                pushw(get(DX))
            case insts.popa:
                set(DX,popw())
                set(CX,popw())
                set(BX,popw())
                set(AX,popw())

            case insts.halt:
                emulator.running = False
        if inst in instcheck:
            check(dest&0xC)

if TYPE_CHECKING: from main import Emulator
