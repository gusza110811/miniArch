import enum

class Instructions(enum.Enum):
    ld   = 0x10
    st   = 0x11
    ldi  = 0x12
    rmov = 0x13
    inp  = 0x14
    out  = 0x15
    movb = 0x19
    movw = 0x1A

    halt= 0xff
