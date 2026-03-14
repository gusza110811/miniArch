import enum

class Instructions(enum.Enum):
    rmov = 0x10
    ldi4 = 0x11
    ldi8 = 0x12
    ldi16= 0x13
    stb  = 0x18
    ldb  = 0x19
    stw  = 0x1A
    ldw  = 0x1B
    inp  = 0x1C
    out  = 0x1D

    halt= 0xff
