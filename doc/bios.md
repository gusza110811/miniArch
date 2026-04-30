# MiniArch BIOS interface definition

## Table of Contents

...

## The BIOS
- Located at F0000-FFFFF
- May use memory at `E8000`-`EFFFF` for its own data

## Boot process
- Check if Disk 0 exists
- Fail boot if it does not
- Otherwise load the first sector into `07c00`
- Then Far Jump to `0000:7c00`
- All segment registers set to 0
- But GPRs and stack registers are not reset, and depends on the BIOS implementation

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
