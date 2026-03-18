; rom code is mapped to F0000-FFFFF
; CS = F000
; DS = SS = ES = 0

func main {
    mov ds, cs  ; CS = DS = F000

    mov bx, val1
    mov ax, [bx]

    add bx, 2
    mov dx, [bx]

    add bx, 2
    mov cx, [bx]

    sub dx, cx

    halt
    end:
    export size = end - main
}
; here, `main` and `size` is defined, but not `end`

val1:   .word 0x80
val2:   .word 0x1108
val3:   .word 0x6502

; expected end state
; ax = 80
; bx = ...
; cx = 6502
; dx = ac06
;
; Negative flag set
