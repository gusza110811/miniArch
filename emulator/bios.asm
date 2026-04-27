func main {
    ; set up segments
    mov ax, 0xF800
    mov ds, ax

    ; startup message
    mov bx, start_msg
    call print

    ; check for disks
    mov bx, 0x0320
    mov ax, 0x03
    out bx, ax
    mov bx, 0x0327
    in ax, bx
    cmp ax, 0
    jz no_disks
    call read

    jmpf 0, 0x7c00
}

func no_disks {
    mov bx, err_msg
    call print
    hlt
}

func read {
    mov bx, 0x0320
    mov ax, 0x05
    out bx, ax
    mov ax, 0x01
    out bx, ax

    ; read buffer
    mov dx, 0x0327
    mov bx, 0x7c00
    mov cx, 512
    read_loop:
        in ax, dx
        mov [b es:bx], ax
        add bx, 1
        sub cx, 1
    jnz read_loop

    ret
}

; bx = pointer to message
func print {
    pusha
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
    popa
    ret
}

.align 0x8000 ; address $8000 in rom (F000:8000)
.org 0 ; but used as if it were at $0000 (F800:0000)
; if ds = $8000 then this will
; give us 32k of space for ro data, and 32k for rw data (address wraps around at 0x10000)
start_msg:
    .asciiz "MiniArch BIOS\n"
err_msg:
    .asciiz "No disks found\n"

.align 0x7FF0 ; because align is relative to the .org, this will be at FFFF:0000 (reset vector)
func reset {
    jmpf 0xf000, main
}
