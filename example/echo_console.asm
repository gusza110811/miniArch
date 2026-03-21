; rom code is mapped to F0000-FFFFF
; CS = FFFF
; DS = SS = ES = 0
const buffer = 0x100

func init {
    mov bx, text
    mov ds, cs
    call print
}

func main {
    mov ds, 0
    mov bx, buffer
    call input
    mov bx, buffer
    call print
    jmp main
}

; cx = buffer
func input {
    mov dx, 0xffff
    in ax, dx
    cmp ax, 0
    jz input

    cmp ax, '\b'
    bz bksp

    cmp ax, '\n'
    jz crlf

    cmp ax, '\r'
    jz crlf

    out dx, ax

    mov [b bx], ax
    add bx, 1
    jmp input
}

func crlf {
    mov cx, '\r'
    out dx, cx
    mov cx, '\n'
    out dx, cx
    mov ax, '\n'
    mov [b bx], ax
    ret
}

; affect cx, bx--
func bksp {
    mov cx, ' '
    out dx, ax
    out dx, cx
    out dx, ax
    sub bx, 1
    mov ax, [b bx]
    jmp input
}

; affects ax, bx, cx, dx
func print {
    mov dx, 0xffff
    mov cx, '\r'
    loop:
        mov ax, [b bx]
        cmp ax, 0
        jz done
        add bx, 1
        cmp ax, '\n'
        jz lfcrlf
        out dx, ax
        jmp loop
    lfcrlf:
        out dx, cx
        out dx, ax
    jmp loop

    done:
    ret
}

text:   .asciiz "Echo Console!!!\n"

.align 0xFFF0
func reset {
    jmpf 0xF000, 0
}

.align 0xFFFF .zero
