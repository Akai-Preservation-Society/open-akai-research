---
id: s3200.address-model
title: How addresses work in OS 2.00 (reset, the RAM copy, segment:offset)
machine: s3200
area: cpu
firmware: ["s3200-v2.00"]
status: static
hardware_tested: no
summary: At reset the 256 KiB image is at physical 0xC0000. The boot block copies it to RAM and the OS runs there, where seg*16+off equals the file offset for every address in the image. Only the boot block and reset vector run from ROM.
contributors: ["open-akai-research"]
last_verified: 2026-11-02
depends_on: ["s3200.eprom-layout"]
---

# How addresses work in OS 2.00 (reset, the RAM copy, segment:offset)

**Required before using any address in this folder.** This is not the
MPC3000's or the MPC2000XL's model; do not carry their addresses here.

## Address forms

| Form | Example | Used for |
|---|---|---|
| File offset | `0x1B2C0` | Pins, patches, the symbol table's `file_offset` |
| Runtime seg:off | `0FE9:B430` | Code, and the symbol table's `address`. `seg*16 + off` = file offset |
| ROM seg:off | `DFE8:00D1`, `FFFF:0000` | Only the boot block and reset vector. Physical = `0xC0000 + file offset` |

## Claims

- **[static]** File `0x3FFF0` holds `EA 00 00 E8 DF` (`JMP FAR DFE8:0000`). For this to be the reset vector at physical `0xFFFF0`, the image sits at physical `0xC0000-0xFFFFF`. `DFE8:0000` is physical `0xDFE80`, file `0x1FE80`, where the boot block begins. A second far jump, `EA D1 00 E8 DF` (`DFE8:00D1`, file `0x1FF51`), follows at `0x3FFF5` ([rom-serial-loader.md](rom-serial-loader.md)).
- **[static]** The boot block (file `0x1FE80-0x1FFD5`) uses V53-only features: it reads the XAM register (port `0xFF80`, bit 0 = extended addressing), writes page registers at ports `0xFF00-0xFF7E`, and executes `BRKXA` (`0F E0 imm8`, at `0x1FECE` and `0x1FF49`) and `RETXA` (`0F F0 imm8`, at `0x1FEAF` and `0x1FF36`). These opcodes do not exist on an 8086 or 80186, so a disassembler that does not know them mis-decodes this area.
- **[static]** Reset path: if XAM bit 0 is clear it tests RAM at `0000:0000`, writes 48 page registers (`0xFF00-0xFF5E`) with `0x40-0x6F` (logical `0x00000-0xBFFFF` to physical `0x100000-0x1BFFFF`) and 16 (`0xFF60-0xFF7E`) with `0x30-0x3F` (logical `0xC0000-0xFFFFF` to ROM), executes `BRKXA 11h`, copies the four 64 KiB banks `C000-F000:0000` to `0000-3000:0000`, sets `[0000:7F60]=1`, saves XAM state at `[0000:7F62]`, `RETXA 12h`, remaps `0xFF60-0xFF7E` to `0x70-0x7F` (logical `0xC0000-0xFFFFF` to RAM at physical `0x1C0000-0x1FFFFF`), `BRKXA 13h`, and jumps to `0000:0000` in the RAM copy.
- **[hypothesis]** The page-register values map 16 KiB pages (value = physical address >> 14). This reading follows from the values written and the V53 family, not from a cited datasheet.
- **[static]** After the copy, logical address = file offset for the whole image `0x00000-0x3FFFF`, and the OS never executes from ROM. Only the boot block issues page-register writes or `BRKXA`/`RETXA`; the OS itself never remaps.
- **[static]** RAM entry: `0000:0000` holds `EB 4E` (jump to `0x50`). `0x50` jumps to `0x53`, which sets DS=ES=SS=0 and SP=`0x200`, copies `[0x1E]` to `[0x1D]` (the version word), installs INT 0 = `2033:0AE3`, and jumps far to `0FE9:0002` (file `0xFE92`), the OS start. A disk-loaded OS enters at `0000:0050`, skipping the `EB 4E` ([os-load-and-save.md](os-load-and-save.md)).
- **[static]** Consequences: the first `0x400` bytes of the copy are the live interrupt vector table and are overwritten at run time; the boot block and reset vector have no effect when an OS is loaded from disk, but do when the same image is burned to EPROM.
- **[documented]** MAME's S3000 map instead switches `0xC0000-0xFFFFF` between ROM and RAM with I/O port `0x68` bit 4 and does not model the page map above. Neither model has been checked against hardware.
- **[open]** What, if anything, lives in physical RAM `0x1C0000-0x1FFFFF` after boot.

## Evidence

- Static: `ndisasm -b16` of the linear image at `0x3FFF0`, `0x1FE80-0x1FFD5`, `0x0-0x84` and `0xFE92`, read 2026-10-21 and re-read 2026-11-02; segment-register and port-immediate census over the whole image for `0xFF00`/`0xFF60` and `0F E0`/`0F F0`. Pins: `0x3FFF0` (10), `0x1FE80` (209 and 342), `0x0` (132), `0xFE92` (6).
- Documented: MAME `s3000.cpp` at `c2caa8969adb`, `s3000_banked_state::control_port_w`.
- No emulator with V53 paging has run the boot block. The emulator runs in other findings start at `0000:0000` with the boot block's hand-off state set by hand.

## Open questions

- [Is the S3200 an XL board, and does it run this image?](../questions/s3200-hardware-and-os.md)
- [Peripheral relocation order and the V53 registers](../questions/peripheral-relocation.md)
