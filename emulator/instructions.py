import enum

class Instructions(enum.Enum):
    # transfer
    rmov = 0x10
    ldi4 = 0x11
    ldi8 = 0x12
    ldi16= 0x13
    stb  = 0x18
    ldb  = 0x19
    stw  = 0x1A
    ldw  = 0x1B
    inp  = 0x1C#
    out  = 0x1D

    # arithmetic & logic
    add  = 0x20
    addi4= 0x21
    addi8= 0x22
    addi = 0x23
    sub  = 0x24
    subi4= 0x25
    subi8= 0x26
    subi = 0x27
    cmp  = 0x28#
    cmpi4= 0x29#
    cmpi8= 0x2A#
    cmpi = 0x2B#
    incax= 0x2C#
    incbx= 0x2D#
    inccx= 0x2E#
    incdx= 0x2F#

    and_ = 0x30#
    andi = 0x31#
    or_  = 0x32#
    ori  = 0x33#
    xor_ = 0x34#
    xori = 0x35#
    shr  = 0x36#
    shri4= 0x37#
    shl  = 0x38#
    shli4= 0x39#
    not_ = 0x3A#
    neg_ = 0x3B#
    sxtbw= 0x3C#

    # control flow
    # ...s -> rel8
    # ...  -> rel16
    # ...a -> abs16
    # ...l -> seg:abs
    # condition encoded in source descriptor
    jmps = 0x40#
    jmp  = 0x41#
    jmpa = 0x42#
    jmpl = 0x43#
    calls= 0x44#
    call = 0x45#
    ret  = 0x46#
    calla= 0x47#
    calll= 0x48#
    retl = 0x49#

    halt = 0xFF

    def __str__(self):
        return self.name
