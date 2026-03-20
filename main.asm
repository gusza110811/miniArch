; rom code is mapped to F0000-FFFFF
; CS = F000
; DS = SS = ES = 0

; print all printable* ascii in reverse
func main {
    mov ax, 127
    mov bx, 0xffff
    loop:
    out bx, ax
    sub ax, 1
    jnz loop

    halt
}

; *this includes special characters from 1-31
