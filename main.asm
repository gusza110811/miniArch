; rom code is mapped to F0000-FFFFF
; CS = F000
; DS = SS = ES = 0

; hardcoded print
; will use call/ret later
func hardprint {
    mov bx, text
    mov dx, 0xffff
    loop:
        mov ax, [b cs:bx]
        cmp ax, 0
        jz init
        out dx, ax
        add bx, 1
    jmp loop
}

func init {
    mov bx, 0xffff
}

func main {
    in ax, bx
    cmp ax, 0
    jz main

    cmp ax, '\n'
    jz crlf

    cmp ax, '\r'
    jz crlf

    cmp ax, '\b'
    jz bksp

    out bx, ax
    jmp main
}

func crlf {
    mov dx, '\r'
    out bx, dx
    mov dx, '\n'
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

text:   .asciiz "Test!!!\r\n"
