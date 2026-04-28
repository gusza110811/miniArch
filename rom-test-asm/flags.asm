func main {
    sta
    sti
    clz
    clc
    cln
    clo
    cli

    halt
}

.org 0xFFF0
func reset {
    jmpf 0xF000, 0
}
