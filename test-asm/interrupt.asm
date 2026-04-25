const dbgconsole = 0xffff

func main {
    mov [w 2*4], ax
    mov [w 2*4 + 2], cs
    mov ax, test
    int 2
    hlt
}

func test {
    mov bx, dbgconsole
    mov ax, '!'
    out bx, ax
    retf
}

.align 0xfff0
func reset {
    jmpf 0xf000, 0x0
}
