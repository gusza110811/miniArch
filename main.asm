; rom code is mapped to F0000-FFFFF
; CS = F000
; DS = SS = ES = 0

func main {
    mov ax, 'H'
    out 0xFFFF, ax
    mov ax, 'e'
    out 0xFFFF, ax
    mov ax, 'l'
    out 0xFFFF, ax
    mov ax, 'l'
    out 0xFFFF, ax
    mov ax, 'o'
    out 0xFFFF, ax
    mov ax, '\n'
    out 0xFFFF, ax

    halt
}
