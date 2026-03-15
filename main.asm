; rom code is mapped to F0000-FFFFF
; CS = F000
; DS = SS = ES = 0

func main {
    ldi ds, 0xf002
    mov bx, val1
    mov ax, [b bx]
    add bx, 2
    mov dx, [bx]
    add bx, 2
    mov cx, [bx]
    sub cx, dx
    halt
}

.align 0x0020
.org 0
data struct {
    val1:   .word 0x80
    val2:   .word 0x1108
    val3:   .word 0x6502
}

; expected end state
; ax = 80
; bx = ...
; cx = 53fa
; dx = 1108
