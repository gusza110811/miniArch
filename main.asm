; rom code is mapped to F0000-FFFFF
; CS = F000
; DS = SS = ES = 0

func main {
    mov bx, val1
    mov ax, [b cs + bx]
    add bx, 2
    mov dx, [cs + bx]
    add bx, 2
    mov cx, [cs + bx]
    halt
}

data struct {
    val1:   .word 0x80
    val2:   .word 0x1108
    val3:   .word 0x6502
}

; expected end state
; ax = 80
; bx = ...
; cx = 6502
; dx = 1108
