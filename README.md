# MiniArch

MiniArch is a custom 16-bit architecture project. includes an assembler for compiling assembly code into machine code and an emulator for executing the resulting programs.

## Project Structure

- **assembler/**: Contains the assembler components

- **emulator/**: Contains the emulator components

- **doc/**: Documentations.

- **examples/**: Example programs

- **rom-examples/**: Example ROM programs

- **test-asm**: Test programs

- **rom-test-asm/**: Test ROM programs

## Features

- Custom 8086-like 16-bit instruction set.
    - Segmented memory access
    - 17 Registers
    - 3 Addressing modes
- Assembler: Assemble assembly code to binary machine code.
- Emulator: Runs the machine code.

## Usage

1. **Assembling Code**:
   - Run the assembler on an .asm file to generate machine code.
   - Example: `python assembler/main.py examples/hello_world.asm`

2. **Emulating Code**:
   - Run the emulator on the generated binary. (as disk image)
   - Example: `python emulator/main.py --hda examples/hello_world.bin`

Refer to `doc/isa.md` for the full instruction set and encoding details.

## Requirements

- POSIX compliant (Linux, BSD, Mac, etc) operating system
    - Attempt to run the emulator on other system (such as Windows) will raise `NotImplementedError: terminal magic does not work with non-posix system`
- Python 3.x
- Lark parser (for assembler)

Install dependencies: `pip install lark`
