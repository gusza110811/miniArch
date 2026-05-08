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
MiniArch supports address operands in three flavors:
- **Direct**

        SEGMENT : immediate

- **Indirect**

        SEGMENT : BX
  Accesses memory at the address stored in `BX`.

- **Indexed**

        SEGMENT : BX + immediate
        SEGMENT : BP + immediate
  Accesses memory at a base register plus a signed offset.

---

## Instruction encoding
This section explains the encoding of a MiniArch instruction.

### Structure
    [OPCODE 1 byte] [DEST/SRC 1 byte] [OPERAND 0-2 bytes]

- `OPCODE` identifies the instruction.
- `DEST/SRC` encodes either registers or a memory address.
- `OPERAND` is present only for instructions that require immediate data.

### Destination & Source encoding
Most instructions use the second byte to encode a destination and source pair,
or to encode an addressing mode for memory access.

#### Encoding Registers
    0: AX, BX, CX, DX
    4: CS, DS, SS, ES
    8: SP, BP
    C: AH, BH, CH, DH

#### Encoding Memory Address
    0: CS:BX , DS:BX , SS:BX , ES:BX
    4: CS:imm, DS:imm, SS:imm, ES:imm
    8: CS:BX+imm , DS:BX+imm , SS:BX+imm , ES:BX+imm
    8: CS:BP+imm , DS:BP+imm , SS:BP+imm , ES:BP+imm
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
2.  [RMOV](#rmov)
3.  [LDI](#ldi)
4.  [ST](#st)
5.  [LD](#ld)
6.  [LEA](#lea)
7.  [ADD](#add)
8.  [ADDI](#addi)
9.  [SUB](#sub)
10. [SUBI](#subi)
11. [CMP](#cmp)
12. [CMPI](#cmpi)
13. [NEG](#neg)
14. [AND](#and)
15. [ANDI](#andi)
16. [OR](#or)
17. [ORI](#ori)
18. [XOR](#xor)
19. [XORI](#xori)
20. [SHR](#shr)
21. [SHRI4](#shri4)
22. [SHL](#shl)
23. [SHLI4](#shli4)
24. [NOT](#not)
25. [JMP](#jmp)
26. [CALL](#call)
27. [RET](#ret)
28. [JMPF](#jmpf)
29. [CALLF](#callf)
30. [RETF](#retf)
31. [INT](#int)
32. [PUSH](#push)
33. [POP](#pop)
34. [PUSHF](#pushf)
35. [POPF](#popf)
36. [PUSHA](#pusha)
37. [POPA](#popa)
38. [STZ](#stz)
39. [STC](#stc)
40. [STN](#stn)
41. [STO](#sto)
42. [STI](#sti)
43. [STA](#sta)
44. [CLZ](#clz)
45. [CLC](#clc)
46. [CLN](#cln)
47. [CLO](#clo)
48. [CLI](#cli)
49. [CLA](#cla)

### NOP
Does nothing

This instruction has 3 forms, 2 of which are equivalent
- `nop0` encoded as `0x00`
- `nop1` encoded as `0x01`
- `nopf` encoded as `0x0F`
    - has the DEST/SRC descriptor but does not do anything with it

### RMOV
Transfer data between registers.

- Encoded as `0x10`.
- `SRC` descriptor selects the source register.
- `DEST` descriptor selects the destination register.

### LDI
Load an immediate value into a register.

This instruction has 3 forms:
- `ldi4` encoded as `0x11`
    - Uses the 4-bit source field as the immediate value.
    - The source nibble is the immediate; the destination nibble selects the register.
- `ldi8` encoded as `0x12`
    - Uses a 1-byte operand after the descriptor.
    - Loads the 8-bit value into the destination register.
- `ldi16` encoded as `0x13`
    - Uses a 2-byte operand after the descriptor.
    - Loads the 16-bit value into the destination register.

### ST
Store a register value into memory.

- `DEST` descriptor selects the memory address operand.
- `SRC` descriptor selects the source register.

This instruction has 2 forms
- `stb` encoded as `0x18`
    - Store the low byte of `SRC` register to memory address `DEST`
- `stw` encoded as `0x1A`
    - Store value of `SRC` register to memory address `DEST`

### LD
Load value from memory

- `DEST` descriptor selects the target register.
- `SRC` descriptor selects the memory address operand.

This instruction has 2 forms:
- `ldb` encoded as `0x19`
    - Load the byte value at the memory address into `DEST`.
- `ldw` encoded as `0x1B`
    - Load the word value at the memory address into `DEST`.

### LEA
Load effective address.

- Encoded as `0x1E`.
- Loads the offset component of a memory address operand relative to DS:0 into the target register.
- Use this to obtain the address of a memory location without performing a memory load.

### ADD
Add 2 registers

- encoded as `0x20`
- `DEST` descriptor encode the target register to add to
- `SRC` descriptor encode the source register to get addend from
- Update `Z`, `C` and `O` flag

### ADDI
Add an immediate value to a register.

- `DEST` descriptor selects the register to update.
- Updates `Z`, `C`, and `O` flags.

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
Subtract an immediate value from a register.

- `DEST` descriptor selects the register to update.
- Updates `Z`, `C`, `N`, and `O` flags.

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
Compare two registers by subtracting the source from the destination and updating flags.

- Encoded as `0x28`
- `DEST` descriptor selects the register that is compared against `SRC`.
- `SRC` descriptor selects the register whose value is subtracted.
- The result is not written back; only flags are updated.
- Updates `Z`, `C`, `N`, and `O`.

### CMPI
Compare a register against an immediate value.

- Encoded as `0x29`, `0x2A`, or `0x2B`.
- `DEST` descriptor selects the register to compare.
- The immediate is subtracted from the register value.
- The result is not written back; only flags are updated.
- Updates `Z`, `C`, `N`, and `O`.

This instruction has 3 forms:
- `cmpi4` encoded as `0x29`
    - Uses the 4-bit source field as the immediate value.
- `cmpi8` encoded as `0x2A`
    - Uses a 1-byte operand after the descriptor.
- `cmpi16` encoded as `0x2B`
    - Uses a 2-byte operand after the descriptor.

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
Branch within the current code segment.

- Encoded as `0x40`.
- The second descriptor byte encodes both the condition and the distance format.
- `SRC` (low 4 bits) encodes the condition.
- `DEST` (high 4 bits) encodes the distance type.

Conditions:

        0: jump if Z == 0
        1: jump if Z == 1
        2: jump if C == 0
        3: jump if C == 1
        4: jump if N == 0
        5: jump if N == 1
        F: always

Distance formats:

        0: relative 8-bit signed displacement
        1: relative 16-bit signed displacement
        2: absolute 16-bit address

For relative jumps, the target address is computed from the current `IP`.

### CALL
Call a subroutine within the current code segment.

- Encoded as `0x41`.
- The second descriptor byte encodes the call condition and the distance format.
- `SRC` (low 4 bits) encodes the condition.
- `DEST` (high 4 bits) encodes the distance type.
- The return address is pushed to the stack before transferring control.

Conditions:

        0: call if Z == 0
        1: call if Z == 1
        2: call if C == 0
        3: call if C == 1
        4: call if N == 0
        5: call if N == 1
        F: always

Distance formats:

        0: relative 8-bit signed displacement
        1: relative 16-bit signed displacement
        2: absolute 16-bit address

### RET
Return from subroutine

- Encoded as `0x42`
- Pop from stack to get the previous `PC`

### JMPF
Far jump to a different code segment.
- Encoded as `0x48`
- Uses a 2-byte operand for target segment
- Uses a 2-byte operand for target code position

### CALLF
Call a subroutine in a different code segment.
- Encoded as `0x49`
- Uses 1 2-byte operand for target segment
- Uses 1 2-byte operand for target code position
- Push `CS` and `PC` to stack

### RETF
Return out of subroutine called from a different segment

- Encoded as `0x4A`
- Pop from stack twice to get the previous `PC` and previous `CS`

### INT
Invoke an interrupt handler.
- Encoded as `0x4B`.
- Uses a 1-byte operand for the interrupt vector number.
- Reads the interrupt vector table at physical address `0x0000`.
- Each vector entry is 4 bytes: offset at `id*4`, segment at `id*4 + 2`.
- Pushes `CS` and `PC` to the stack before jumping to the handler.

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
