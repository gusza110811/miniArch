import enum

class Instructions(enum.Enum):
    ld  = 0x10
    st  = 0x11
    mov = 0x12
    rmov= 0x13
    inp = 0x14
    out = 0x15

    halt= 0xff
