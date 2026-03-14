; rom code is mapped to F0000-FFFFF
; CS = F000
; DS = SS = ES = 0

func main {
    mov ax, [b cs+val1] ; ldb dest=ax src=cs+imm, (val1)
    mov bx, [cs+val2]   ; ldw dest=bx src=cs+imm, (val1)
    mov [b 0], bx       ; stb dest=ds+imm src=bx, 0
    mov cx, [b 0]       ; ldb dest=cx src=ds+imm, 0
    halt                ; halt
}

data struct {
    val1:   .byte 0x18
    val2:   .word 0x1108
}

; expected end state
; ax = 18
; bx = 1108
; cx = 8
; ...
; [00000] = 8
