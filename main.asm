; rom code is mapped to F0000-FFFFF
; CS = F000
; DS = SS = ES = 0

func main {
    console = 0xffff

    mov ax, 'H'
    out console, ax
    mov ax, 'e'
    out console, ax
    mov ax, 'l'
    out console, ax
    mov ax, 'l'
    out console, ax
    mov ax, 'o'
    out console, ax
    mov ax, '\r'
    out console, ax
    mov ax, '\n'
    out console, ax

    halt
}
