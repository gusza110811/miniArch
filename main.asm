; rom code is mapped to F0000-FFFFF
; CS = F000
; DS = SS = ES = 0

; print all printable* ascii in reverse
func init {
    mov bx, 0xffff
    ; falls through into main
}

func main {
    in ax, bx
    cmp ax, 0
    jz main

    cmp ax, '\n'
    jz lfcrlf

    cmp ax, '\r'
    jz crcrlf

    cmp ax, '\b'
    jz bksp

    out bx, ax
    jmp main
}

func lfcrlf {
    mov dx, '\r'
    out bx, dx
    out bx, ax
    jmp main
}

func crcrlf {
    mov dx, '\n'
    out bx, ax
    out bx, dx
    jmp main
}

func bksp {
    mov dx, ' '
    out bx, ax
    out bx, dx
    out bx, ax
    jmp main
}
