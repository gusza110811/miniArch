func main {
    ; set up segment
    mov ax, 0xE800
    mov ds, ax
    mov ax, 0x1000
    mov ss, ax
    mov ax, 0
    mov es, ax

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

    ; add interrupt services
    mov ax, serial_port_srv
    mov [es:0x14 * 4], ax
    mov [es:0x14 * 4 + 2], cs

    call read

    ; reset segments
    mov ds, 0
    mov es, 0
    mov ss, 0

    jmpf 0, 0x7c00
}

func no_disks {
    mov bx, nodisk_err
    call print
    hlt
}

; 0x13 service
; dx = command
func disk_srv {

    cmp dx, 1
    jz status
    cmp dx, 2
    jz read

    cmp dx, 3
    jz sector

    retf

    ; ax -> status
    func status {
        push bx
        mov bx, 0x321
        in ax, bx
        pop bx
        retf
    }

    ; bx <- start of 512 bytes region in memory to write to
    ; ax -> status (0 = success. 1 = fail)
    func read {
        push dx

        mov dx, 0x320
        mov ax, 1
        out dx, ax

        ; wait
        wait:
            mov dx, 0x321
            in ax, dx
            cmp ax, 1
        jz wait

        cmp ax, 0
        jnz fail

        ; read buffer
        mov dx, 0x0327
        mov cx, 512
        read_loop:
            in ax, dx
            mov [b bx], ax
            add bx, 1
            sub cx, 1
        jnz read_loop

        pop dx
        mov ax, 0
        retf

        fail:
            mov ax, 1
        retf
    }

    ; ax = sector (lower word)
    ; bx = sector (upper word)
    func sector {
        push dx

        mov dx, 0x322
        out dx, ax
        mov dx, 0x323
        out dx, ah
        mov dx, 0x324
        out dx, bx
        mov dx, 0x325
        out dx, bh

        pop dx
        retf
    }
}

; 0x14 service
; dx = command
func serial_port_srv {
    cmp dx, 1
    jz sput_char
    cmp dx, 2
    jz sget_char
    retf

    func sput_char {
        push bx
        mov bx, 0xFFFF
        out bx, ax
        pop bx
        retf
    }

    func sget_char {
        push bx
        mov bx, 0xFFFF
        in ax, bx
        pop bx
        retf
    }

}

func read {
    mov bx, 0x0320
    mov ax, 0x05
    out bx, ax
    mov ax, 0x01
    out bx, ax

    ; wait
    wait:
    mov bx, 0x321
    in ax, bx
    cmp ax, 1
    jz wait

    ; check if success
    cmp ax, 0
    jnz fail

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

    fail:
        mov bx, diskfail_err
        call print
        hlt
}

; bx = pointer to message
func print {
    pusha
    mov dx, 0xffff
    loop:
        mov ax, [b bx]
        cmp ax, 0
        jz done
        add bx, 1
        out dx, ax
    jmp loop

    done:
    popa
    ret
}

{
    .offset 0x8000
    ; if ds = E800
    ; 32k of space for rw data, and 32k for ro data
    export start_msg:
        .asciiz "MiniArch BIOS\r\n\r\n\r\n"
    export nodisk_err:
        .asciiz "Disk 0 not available\r\n"
    export diskfail_err:
        .asciiz "Failed to load boot sector\r\n"
}

.org 0xFFF0
func reset {
    jmpf 0xf000, main
}
