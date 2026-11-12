---
id: mpc3000.address-model
title: How addresses work on the MPC3000 (V53 extended addressing)
machine: mpc3000
area: cpu
firmware: ["mpc3000-v3.08", "mpc3000-v3.11", "mpc3000-v3.12", "mpc3000-vailixi-3.50"]
status: static
hardware_tested: no
summary: The five address forms used in this repository, how the V53 page registers turn a 20-bit address into a 24-bit one, and the three page tables the firmware loads.
contributors: ["open-akai-research"]
last_verified: 2026-09-23
sources: ["NEC 16-bit V-Series Microprocessor Data Book (1991)", "MAME devices/cpu/nec (v33_translate, v5x.cpp)", "MAME src/mame/akai/mpc3000.cpp"]
depends_on: ["mpc3000.memory-and-io-map", "mpc3000.eprom-layout"]
---

# How addresses work on the MPC3000

A correct instruction at the wrong address spoils everything built on it.
Read this before using any address in this machine's section.

## The five address forms

| Form | Meaning | Example |
|---|---|---|
| Chip-file offset | Position inside one 256 KiB EPROM dump (LS or MS) | never use as a CPU address |
| Linear file offset | Position in the interleaved 512 KiB image. **The form used by symbols, pins and patches** | `0x7FFF0` |
| Segment:offset | What the code uses, `CS:IP` or `DS:offset` | `B000:01A7` |
| 20-bit address | `(segment << 4) + offset`, the 8086 address | `0xB01A7` |
| 24-bit physical | Where the 20-bit address lands after the page registers | `0x300044` |

For code in ROM: `linear file offset = ((segment << 4) + offset) & 0x7FFFF`.
Chip-file offset = linear file offset / 2 (even bytes are in the LS chip,
odd bytes in the MS chip).

## Claims

- **[documented]** At reset the V53 starts at `FFFF:0000` with extended addressing off. The first fetch is 20-bit `0xFFFF0`, linear file offset `0x7FFF0`.
- **[documented]** The 512 KiB ROM appears twice in the first megabyte (`0x00000-0x7FFFF` and `0x80000-0xFFFFF`), which is why the formula above masks with `0x7FFFF`.
- **[documented]** With extended addressing on (XA=1), the top six bits of the 20-bit address pick one of 64 page registers at I/O `0xFF00-0xFF7E`, and `24-bit = (register << 14) | (20-bit & 0x3FFF)`. Each page is 16 KiB. The whole 16-bit register is shifted.
- **[documented]** Two V53-only instructions switch the mode: `BRKXA imm8` (`0F E0 ib`) and `RETXA imm8` (`0F F0 ib`). Both fetch interrupt vector `imm8` in the mode that is current before the switch.
- **[static]** Boot code at `FAC0:0000` writes 64 words from linear `0x7AE56` to the page registers, then executes `BRKXA 11h`. From then on the machine runs with XA=1.
- **[static]** The firmware holds three page tables. Their bytes are identical in 3.11, 3.12 and Vailixi 3.50 at linear `0x7AE56` (first), `0x7ACB4` (second) and `0x7ADCF` (third). In 3.08 the third table has the same bytes at `0x7AD29`; the other two were not located.
- **[static]** What each table maps (page number = 20-bit address / 16 KiB):

  | 20-bit range | Pages | First table (early boot) | Second table (OS running) | Third table (after `INT 10h`) |
  |---|---|---|---|---|
  | `0x00000-0x9FFFF` | 0-39 | RAM `0x300000+` | RAM `0x300000+` | RAM `0x300000+` |
  | `0xA0000-0xAFFFF` | 40-43 | ROM (file `0x20000+`) | RAM | RAM |
  | `0xB0000-0xF3FFF` | 44-60 | ROM (file `0x30000-0x73FFF`) | ROM (file `0x30000-0x73FFF`) | **RAM** `0x3B0000-0x3F3FFF` |
  | `0xF4000-0xF7FFF` | 61 | `0x500000` (NVRAM) | `0x500000` (NVRAM) | `0x500000` (NVRAM) |
  | `0xF8000-0xFFFFF` | 62-63 | ROM (file `0x78000-0x7FFFF`) | same | same |

- **[static]** Consequence: once the first table is loaded, segment `0000` is RAM. The live interrupt vector table is in RAM at 24-bit `0x300000`; the vectors at the start of the ROM are only used before the switch.
- **[static]** Consequence: while the OS runs, segments `B000`-`F3FF` are OS code in ROM and segments `F800`-`FFFF` are the BIOS, kernel and boot code in ROM. Under the third table the OS code range becomes RAM and only the BIOS range stays ROM.
- **[static]** The boot code also relocates the CPU's on-chip peripherals: it writes `OPHA=0xC0`, `DULA=0x00`, `IULA=0x10`, `SULA=0x20`, `TULA=0x30`, `OPSEL=0x0F` to the fixed system ports at `0xFFE0-0xFFFE`. That is why I/O ports `0xC0xx` appear in the BIOS.
- **[hypothesis]** Which on-chip unit each relocated `0xC0xx` port belongs to, bit by bit, has not been checked against the NEC manual.
- **[open]** Whether any OS code rewrites a page register while running, outside the three table loads. Two sites that could are listed in [the question](../questions/page-register-writes-at-runtime.md).
- **[hypothesis]** Other Akai machines with the same CPU map their ROM differently. Do not carry file-offset arithmetic from another machine into this one, or from this one into another.

## Evidence

- CPU behaviour (reset state, translation formula, `BRKXA`/`RETXA` encodings): NEC V-Series data book and the MAME NEC core, which implements the same rules.
- Table contents: read from the images and decoded as 64 little-endian words. The three tables are pinned in [../pins/](../pins/), so `python3 tools/oar.py verify <firmware-id> <image>` confirms your image carries the same tables.
- The boot write sequence and the relocation register values come from static decoding of `mpc3000-vailixi-3.50` (analysis dated 2026-09-21 to 2026-09-23). Table bytes were re-compared across the four images on 2026-11-13.
- No part of this has been observed on a board; an emulator boot that reaches the OS is consistent with it.

## Open questions

- [Page-register writes at run time](../questions/page-register-writes-at-runtime.md)
- [Ports C010h and C011h](../questions/icu-ports-c010-c011.md)
- [PAL address decode](../questions/pal-address-decode.md)
