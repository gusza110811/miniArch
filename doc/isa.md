# MiniArch Instruction Set Specification

Table of Content
1. [Internal Specification](#internal-specification)
2. [Instruction Encoding](#instruction-encoding)
4. [Opcode Definition](#opcode-definition)

## Internal Specification

### Registers
MiniArch has 17 registers

10 WORD registers
- General Purpose
    - `AX` Accumulator
    - `BX` Base
    - `CX` Counter
    - `DX` Data
- Segment
    - `CS` Code Segment
    - `DS` Data Segment
    - `SS` Stack Segment
    - `ES` Extra Segment
- Stack
    - `SP` Stack Pointer
    - `BP` Base Pointer

4 BYTE registers: 
- `AH` (High byte of AX)
- `BH` (High byte of BX)
- `CH` (High byte of CX)
- `DH` (High byte of DX)

All the above can be used in any instruction with minimal limitation

Below are registers that cannot be used directly

2 INTERNAL WORD registers:
- `PC`: Program Counter, points to the next instruction
- `IP`: Instruction Pointer, points to the current instruction

1 INTERNAL BYTE register:
- `FLAGS`: Status Flags
    - 0 Zero
    - 1 Carry
    - 2 Negative
    - 3 Sign Overflow
    - 4 Interrupt Enable

### Addressing
MiniArch has 3 addressing modes:
- **Indirect**

        SEGMENT : BX
- **Direct**

        SEGMENT : immediate
- **Indexed**

        SEGMENT : BX + immediate

---

## Instruction encoding
This section explains the encoding of an instruction in MiniArch

### Structure
    [OPCODE 1 byte] [DEST/SRC 1 byte] [OPERAND 1-2 bytes]
- OPCODE
    - encode the instruction id
- DEST/SRC (used in most instructions)
    - encode the destination and source of the values
- OPERAND (used in some case)
    - usually encode the immediate value to be used by the operation

### Destination & Source encoding
Most instruction use them to encode registers or to encode memory address to get/put the value

#### Encoding Registers
    0: AX, BX, CX, DX
    4: CS, DS, SS, ES
    8: SP, BP
    C: AH, BH, CH, DH

#### Encoding Memory Address
    0: CS:BX , DS:BX , SS:BX , ES:BX
    4: CS:imm, DS:imm, SS:imm, ES:imm
    8: CS:BX+imm , DS:BX+imm , SS:BX+imm , ES:BX+imm
addressing with `imm` will take a 2-bytes operand

---

## Boot
### Initial State
- `CS` = `FFFF`
- Every other register = 0
- Memory F0000-FFFFF is mapped to ROM

### Reset Vector
- 16 bytes of code at `FFFF0`
- should contain a `JMPF` to the main program

## Opcode Definition
1.  [NOP](#nop)
2.  [RMOW](#rmov)
3.  [LDI](#ldi)
4.  [ST](#st)
5.  [LD](#ld)
6.  [ADD](#add)
7.  [ADDI](#addi)
8.  [SUB](#sub)
9.  [SUBI](#subi)
10. [CMP](#cmp)
11. [CMPI](#cmpi)
12. [NEG](#neg)
13. [AND](#and)
14. [ANDI](#andi)
15. [OR](#or)
16. [ORI](#ori)
17. [XOR](#xor)
18. [XORI](#xori)
19. [SHR](#shr)
20. [SHRI4](#shri4)
21. [SHL](#shl)
22. [SHLI4](#shli4)
23. [NOT](#not)
24. [JMP](#jmp)
25. [CALL](#call)
26. [RET](#ret)
27. [JMPF](#jmpf)
28. [CALLF](#callf)
29. [RETF](#retf)
30. [PUSH](#push)
31. [POP](#pop)
32. [PUSHF](#pushf)
33. [POPF](#popf)
34. [PUSHA](#pusha)
35. [POPA](#popa)
36. [STZ](#stz)
37. [STC](#stc)
38. [STN](#stn)
39. [STO](#sto)
40. [CLZ](#clz)
41. [CLC](#clc)
42. [CLN](#cln)
43. [CLO](#clo)
44. [CLI](#cli)
45. [CLA](#cla)

### NOP
Does nothing

This instruction has 3 forms, 2 of which are equivalent
- `nop0` encoded as `0x00`
- `nop1` encoded as `0x01`
- `nopf` encoded as `0x0F`
    - has the DEST/SRC descriptor but does not do anything with it

### RMOV
Transfer data between registers

- Encoded as `0x10`
- `SRC` descriptor encode the source register of the value
- `DEST` descriptor encode the target register to save the value to

### LDI
Load immediate value into a register

This instruction has 3 forms
- `ldi4` encoded as `0x11`
    - Load value of `SRC` as immediate value into register `DEST`
- `ldi8` encoded as `0x12`
    - Has a 1-byte operand
    - Load the operand into register `DEST`
- `ldi16` encoded as `0x13`
    - Has a 2-bytes operand
    - Load the operand into register `DEST`

### ST
Store value into memory

- `DEST` descriptor encode the address of memory to store the value to
- `SRC` descriptor encode the source register

This instruction has 2 forms
- `stb` encoded as `0x18`
    - Store the low byte of `SRC` register to memory address `DEST`
- `stw` encoded as `0x1A`
    - Store value of `SRC` register to memory address `DEST`

### LD
Load value from memory

- `DEST` descriptor encode the target register
- `SRC` descriptor encode the address of memory to load the value from

This instruction has 2 forms
- `ldb` encoded as `0x19`
    - Load the value at memory address `SRC` into `DEST` register
- `ldw` encoded as `0x1B`
    - Load the 2-bytes value at memory address `SRC` into `DEST` register

### ADD
Add 2 registers

- encoded as `0x20`
- `DEST` descriptor encode the target register to add to
- `SRC` descriptor encode the source register to get addend from
- Update `Z`, `C` and `O` flag

### ADDI
Add immediate value to a register

- `DEST` descriptor encode the target register to add to
- Update `Z`, `C` and `O` flag

This instruction has 3 forms
- `addi4` encoded as `0x21`
    - Add value of `SRC` as immediate value to register `DEST`
- `addi8` encoded as `0x22`
    - Has a 1-byte operand
    - Add the operand into register `DEST`
- `addi16` encoded as `0x23`
    - Has a 2-byte operand
    - Add the operand into register `DEST`

### SUB
Subtract 2 registers

- encoded as `0x24`
- `DEST` descriptor encode the target register to subtract to
- `SRC` descriptor encode the source register to subtract by
- Update `Z`, `C`, `N` and `O` flag

### SUBI
Subtract immediate value from a register

- `DEST` descriptor encode the target register to add to
- Update `Z`, `C`, `N` and `O` flag

This instruction has 3 forms
- `subi4` encoded as `0x25`
    - Subtract value of `SRC` as immediate value from register `DEST`
- `subi8` encoded as `0x26`
    - Has a 1-byte operand
    - Subtract the operand from register `DEST`
- `subi16` encoded as `0x27`
    - Has a 2-byte operand
    - Subtract the operand from register `DEST`

### CMP
Compare 2 registers

- encoded as `0x28`
- `DEST` descriptor encode the target register to subtract to
- `SRC` descriptor encode the source register to subtract by
- Doesnt save result but update flags
- Update `Z`, `C`, `N` and `O` flag

### CMPI
Compare immediate value to a register

- `DEST` descriptor encode the target register to add to
- Doesnt save result but update flags
- Update `Z`, `C`, `N` and `O` flag

This instruction has 3 forms
- `cmpi4` encoded as `0x29`
    - Subtract value of `SRC` as immediate value from register `DEST`
- `cmpi8` encoded as `0x2A`
    - Has a 1-byte operand
    - Subtract the operand from register `DEST`
- `cmpi16` encoded as `0x2B`
    - Has a 2-byte operand
    - Subtract the operand from register `DEST`

### NEG
Negate a register

- `DEST` descriptor encode the register to negate the value of
- Encoded as `0x2C`


### AND
Perform bitwise AND on 2 register

    DEST = DEST & SRC
- `DEST` and `SRC` encodes a register
- Encoded as `0x30`

### ANDI
Perform bitwise AND on a register with an immediate value

    DEST = DEST & val
- `DEST` encodes a register
- `val` is a 2 byte operand
- Encoded as `0x31`

### OR
Perform bitwise OR on 2 register

    DEST = DEST | SRC
- `DEST` and `SRC` encodes a register
- Encoded as `0x32`

### ORI
Perform bitwise OR on a register with an immediate value

    DEST = DEST | val
- `DEST` encodes a register
- `val` is a 2 byte operand
- Encoded as `0x33`

### XOR
Perform bitwise XOR on 2 register

    DEST = DEST ^ SRC
- `DEST` and `SRC` encodes a register
- Encoded as `0x34`

### XORI
Perform bitwise XOR on a register with an immediate value

    DEST = DEST ^ val
- `DEST` encodes a register
- `val` is a 2 byte operand
- Encoded as `0x35`

### SHR
Perform logical shift right on a register

    DEST = DEST >> SRC
- `DEST` and `SRC` encodes a register
- Encoded as `0x36`

### SHRI4
Perform logical shift right on a register

    DEST = DEST >> SRC
- `SRC` is the 4bit immediate value
- Encoded as `0x37`

### SHL
Perform logical shift left on a register

    DEST = DEST << SRC
- `DEST` and `SRC` encodes a register
- Encoded as `0x38`

### SHLI4
Perform logical shift left on a register

    DEST = DEST << SRC
- `SRC` is the 4bit immediate value
- Encoded as `0x39`

### NOT
Perform bitwise NOT on a register
    DEST = ~DEST
- `DEST` encodes a register
- Encoded as `0x3A`

### JMP
Pass control to another position within the same code segment

- Encoded as `0x40`
- Uses a 2-byte operand for target

- `SRC` encode condition

        0: On zero, On not zero, On carry, On not carry
        4: On negative, On not negative, On signed overflow, On no signed overflow
        F: Always

- `DEST` encode distance

        0: relative 8 bit
        1: relative 16 bit
        2: absolute 16 bit

### CALL
Call a subroutine within the same code segment

- Encoded as `0x41`
- Uses a 2-byte operand for target
- Push `PC` to stack

- `SRC` encode condition

        0: On zero, On not zero, On carry, On not carry
        4: On negative, On not negative, On signed overflow, On no signed overflow
        F: Always

- `DEST` encode distance

        0: relative 8 bit
        1: relative 16 bit
        2: absolute 16 bit

### RET
Return from subroutine

- Encoded as `0x42`
- Pop from stack to get the previous `PC`

### JMPF
Call a subroutine in a different code segment
- Encoded as `0x48`
- Uses 1 2-byte operand for target segment
- Uses 1 2-byte operand for target code position

### CALLF
Pass control to another position in a different code segment
- Encoded as `0x49`
- Uses 1 2-byte operand for target segment
- Uses 1 2-byte operand for target code position
- Push `CS` and `PC` to stack

### RETF
Return out of subroutine called from a different segment

- Encoded as `0x4A`
- Pop from stack twice to get the previous `PC` and previous `CS`

### PUSH
Push value to stack

- `SRC` encode the source register
- This instruction has 2 forms
    - `pushw` encoded as `0x50`
        - Push the value as 2 byte to stack
        - Decrement `SP` by 2
    - `pushb` encoded as `0x51`
        - Push the value as 1 byte to stack
        - Decrement `SP` by 1

### POP
Pop value from stack

- `DEST` encode the target register
- This instruction has 2 forms
    - `popw` encoded as `0x52`
        - Pop 2 byte from stack and save to `DEST`
        - Increment `SP` by 2
    - `popb` encoded as `0x53`
        - Pop 1 byte from stack and save to `DEST`
        - Increment `SP` by 1

### PUSHF
Push status flag as 8 bit value to stack

- Encoded as `0x54`

        bit     0   1   2   3   4
        flag    Z   C   N   O   I

### POPF
Pop from stack and save to status flags

- Encoded as `0x55`

        bit     0   1   2   3   4
        flag    Z   C   N   O   I

### PUSHA
Push AX, BX, CX and DX to stack

- Encoded as `0x5E`

### STZ
Set `Z` flag to true

- Encoded as `0x60`

### STC
Set `C` flag to true

- Encoded as `0x61`

### STN
Set `N` flag to true

- Encoded as `0x62`

### STO
Set `O` flag to true

- Encoded as `0x63`

### STI
Set `I` flag to true

- Encoded as `0x64`

### STA
Set `Z`, `C`, `N` and `O` flag to true

- Encoded as `0x67`

### CLZ
Clear `Z` flag to false

- Encoded as `0x68`

### CLC
Clear `C` flag to false

- Encoded as `0x69`

### CLN
Clear `N` flag to false

- Encoded as `0x6A`

### CLO
Clear `O` flag to false

- Encoded as `0x6B`

### CLI
Clear `I` flag to false

- Encoded as `0x6C`

### CLA
Clear `Z`, `C`, `N` and `O` flag to false

- Encoded as `0x6F`

### POPA
Pop from stack to DX, CX, BX and AX

- Encoded as `0x5F`
