; rom code is mapped to F0000-FFFFF
; CS = F000
; DS = SS = ES = 0

func init {
    mov bx, text
    mov ds, cs
    call print
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

func print {
    mov dx, 0xffff
    loop:
        mov ax, [b bx]
        cmp ax, 0
        jz done
        out dx, ax
        add bx, 1
    jmp loop
    done:   ret
}

text:   .asciiz "Echo Console!!!\r\n"
