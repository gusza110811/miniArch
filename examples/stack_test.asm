func main {
    mov ax, 0x1108
    push ax
    push al
    push ah
    pop bl
    pop dl
    pop cx
    halt
}

; expected end state
; ax = 1108
; bx = 11
; cx = 1108
; dx = 08

.align 0xfff0
func reset {
    jmpf 0xf000, 0x0
}
