# MiniArch

MiniArch is a custom 16-bit CPU architecture designed for educational and experimental purposes. It features a simple instruction set, memory management, and I/O devices, currently implemented with a Python-based assembler and emulator.

## Components

- **Assembler** (https://github.com/gusza110811/miniArch-as-py): A Python-based assembler that translates MiniArch assembly code (`.asm` files) into executable binary (`.bin` files).
- **Virtual Machine** (https://github.com/gusza110811/miniArch-vm-py): A Python-based virtual machine that executes MiniArch binaries, simulating the CPU, memory, and I/O devices.
- **Specification** (You are here): Specifications for the MiniArch architecture.

## Architecture Overview

MiniArch is a 16-bit architecture with:
- 17 registers (10 word registers, 4 byte registers, 3 internal)
- Support for direct, indirect, and indexed memory addressing
- A rich instruction set for arithmetic, logic, control flow, and I/O operations
- Built-in devices: UART console\*, programmable timers\*, disk controller, debug console

For detailed specifications, see [ISA Specification](spec/isa.md) and [Device Specification](spec/device.md).

## Getting Started

**This assumes you already followed the installation guide for the assembler and virtual machine**

1. **Assemble a program:**
    ```bash
    ma-as <input.asm>
    ```

2. **Run in virtual machine:**
    ```bash
    ma-vm --rom <path/to/rom.bin>
    ```
    for rom binary, or
    ```bash
    ma-vm --hda <path/to/disk_image.img>
    ```
    for disk image

## License

normal copyright law applies because i havent chosen what license to use
