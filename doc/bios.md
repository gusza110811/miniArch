# MiniArch BIOS interface definition

## Table of Contents

...

## The BIOS
- Located at F0000-FFFFF
- May use memory at `E8000`-`EFFFF` for its own data

## Boot process
- Check if Disk 0 exists by querying the disk controller
- Fail boot if it does not exist
- Otherwise load the first sector into `07C00`
- Set up interrupt vector table with serial console service (0x14)
- Then Far Jump to `0000:7C00`
- Segment registers reset to 0
- GPRs and stack registers are not reset by the BIOS; the bootloader is responsible for initialization

## Services

### Serial Console Service
- interrupt id `0x14`
- `DX` determines command

#### Put Character
- `DX` = 1
- Character to print in `AX`

#### Get Character
- `DX` = 2
- Input character returned in `AX`
