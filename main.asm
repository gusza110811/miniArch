; rom code is mapped to F0000-FFFFF
; CS = F000
; DS = SS = ES = 0
; realistically i would later have CS = FFFF
; once i finish implementing most stuff

func main {
    console = 0xffff    ; this is not the port of a real console btw
    ; its more of a debug console where bytes read/written to it is directly connected to the emulator's stdin/out

    mov bx, console

    mov ax, 'H'
    out bx, ax
    mov ax, 'e'
    out bx, ax
    mov ax, 'l'
    out bx, ax
    mov ax, 'l'
    out bx, ax
    mov ax, 'o'
    out bx, ax
    mov ax, '\r'
    out bx, ax
    mov ax, '\n'
    out bx, ax

    halt
}
; constants and label are scoped, so `console` doesnt exist here
; i could put `export console` or just use `export console = 0xffff`
; to put it in the parent scope (in this case, global)
