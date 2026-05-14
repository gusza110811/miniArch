# Device Specifications
The devices usable from the standard MiniArch emulator are often non-standard device.
So this document will try to clarify the usage of these devices

But heads up: you should probably use the BIOS services instead, see [the bios documentations](/doc/bios.md)

## Device mapping
    0300-030F : UART Console*
    0310-031F : Programmable Timers*
    0320-0327 : Disks Controller
    FFFF      : Debug Console

## Devices

### Disk Controller
- Ports

        0320 : Command
        0321 : Status (Read-only)
        0322 : Sector Byte 0
        0323 : Sector Byte 1
        0324 : Sector Byte 2
        0325 : Sector Byte 3
        0326 : Device
        0327 : Data (2-way)

- Commands

    - Read
        - Command `1`
        - Read 512 bytes of data at the specified sector of the specified device
        - Outputs into buffer
        - Set status to busy (`1`) until finished
    - Write
        - Command `2`
        - Write 512 bytes of data to the specified sector of the specified device
        - Reads from buffer
        - Set status to busy (`1`) until finished
    - Query Device
        - Command `3`
        - Query availability of the 256 devices
        - Outputs 256 bytes representing the 256 devices
        - Bit 0 represent usability, 0 means unusable, 1 means usable
    - Query Size
        - Command `4`
        - Query the size of the current device in sectors (4 bytes little endian)
    - Clear Buffer
        - Command `5`
        - Clears the buffer

- Status

    00 : success
    01 : busy
    10 : invalid sector
    11 : invalid device

### Debug Console
Asynchronous console

- Write to port `FFFF` to output a character
- Read from port `FFFF` to get a character from buffer
