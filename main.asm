; rom code is mapped to F0000-FFFFF
; CS = F000
; DS = SS = ES = 0

func main {
    mov ax, [b cs+val1]
    mov bx, [cs+val2]
    mov [b 0], bx
    mov cx, [b 0]
    halt
}

data struct {
    val1:   .byte 0x18
    val2:   .word 0x1108
}
