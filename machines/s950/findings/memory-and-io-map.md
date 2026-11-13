---
id: s950.memory-and-io-map
title: S950 memory map, RAM mapper and I/O decode from Akai's schematics
machine: s950
area: memory
firmware: ["hardware"]
status: documented
hardware_tested: no
summary: The CPU sees four banked 64 KiB RAM windows (0x00000-0x3FFFF, repeated at 0x40000) and the 64 KiB OS ROM at 0x80000-0xFFFFF. Bank registers at I/O 0x1C0-0x1C6 drive physical A16-A23. Three 74HC138s decode I/O; every select matches MAME.
contributors: ["open-akai-research"]
last_verified: 2026-11-13
sources: ["Akai S950 Schematic Diagrams and PC Boards: CPU PCB (1/2) No. 6-2 L601302M and CPU PCB (2/2) No. 6-3 L601303M (scanned; as hosted on s950fx.com, downloaded 2026-11-13)", "MAME src/mame/akai/s900.cpp at commit c2caa8969adb"]
depends_on: ["s950.hardware-overview"]
---

# S950 memory map, RAM mapper and I/O decode from Akai's schematics

Where RAM, ROM and every I/O device sit for the S950's V30, read from
the CPU-board schematics and checked against MAME. Tables:
[../hardware/memory-map.csv](../hardware/memory-map.csv) and
[../hardware/io-ports.csv](../hardware/io-ports.csv).

## Claims

### CPU memory space

- **[documented]** The V30's multiplexed bus is latched by IC15 (A0-A7), IC16 (A8-A15) and IC17. IC17 latches AD16, AD17 and AD19; CPU A18 is not latched.
- **[documented]** RAM is reached through a mapper. IC61 and IC62 are 74HC670 4 x 4 register files, used together as four 8-bit bank registers.
  - Latched CPU A16-A17 (IC17 Q0, Q1) drive their read address.
  - Their outputs are physical A16-A19 (IC61) and A20-A23 (IC62).
  - So each 64 KiB CPU window `0x00000`, `0x10000`, `0x20000`, `0x30000` maps to any 64 KiB page of a 16 MiB physical space.
  - CPU A18 is unused, which is why MAME repeats the windows at `0x40000-0x7FFFF`.
- **[documented]** The bank registers are written from D0-D7 through `-MAP`, the IC23 output for I/O `0x1C0`. A1-A2 choose the register, so the four windows' registers are at I/O `0x1C0`, `0x1C2`, `0x1C4` and `0x1C6`. This matches MAME's `bank_w` (`offset & 3`, even bytes).
- **[documented]** The OS EPROMs: IC12 drives D0-D7 and IC11 drives D8-D15, both addressed by CPU A1-A15. The OS is a 64 KiB word-wide ROM, consistent with the chip files in [../firmware.toml](../firmware.toml).
- **[hypothesis]** The ROM is selected whenever latched CPU A19 is 1, so it repeats every 64 KiB from `0x80000` to `0xFFFFF`, as MAME maps it. The chip-enable net was not traced to IC17's A19 output. The S950 reset vector at linear `0xFFF0` jumps to `F000:FF80`, which only works if the ROM appears at the top of memory ([rom-images.md](rom-images.md)).

### Physical RAM

- **[documented]** Physical A19-A21 go to IC89 (CD74AC138), whose eight outputs are `-CAS0` to `-CAS7`. Each CAS bank is 512 KiB (256K words, physical A1-A18, multiplexed to 9 row and 9 column bits by IC82-IC84). The CAS decode covers 4 MiB; physical A22-A23 go only to the expansion connectors.
- **[documented]** On-board DRAM is seven MB81C4256 (256K x 4):
  - IC45-IC48 form one full 16-bit bank (D0-D15), 512 KiB;
  - IC49-IC51 sit on D4-D15 only, a 256K x 12-bit bank.
- **[hypothesis]** The 12-bit bank holds sample data only, which is 12 bits wide on this machine, while programs and data that need 16 bits use the full bank. Reason: the missing D0-D3 chip and the 12-bit converters. Test: trace which CAS line each bank uses, or watch where the OS puts code.
- **[documented]** The two expansion connectors (J108, J109; the EXM006 boards) carry AD3-AD15, not AD0-AD2. They also carry RA0-RA8, A22, A23, RAS, MRD, LSW, MSW and a set of CAS lines: J109 CAS0-2 and CAS4-7 with its CAS3 pin not connected; J108 CAS0-3, CAS6 and CAS7 with its CAS4 and CAS5 pins not connected. So expansion memory is sample-width, and each slot is wired to different banks.
- **[open]** Which CAS banks the on-board DRAM uses, and so where on-board RAM sits in the physical space. Not traced.
- **[open]** How the owner's manual's "750 KB" relates to the 512 KiB + 256K x 12-bit on-board banks.

### I/O space

- **[documented]** I/O is decoded by three 74HC138s on A3-A8, so ports from `0x200` up repeat the map below:
  - IC22 serves `0x00-0x3F` in 8-byte blocks. It is enabled by `-SLOW` (an OR of A7 and an I/O signal, IC33) and A6 = 0.
  - IC69 serves `0x40-0x7F` in 8-byte blocks. Enabled by A6 = 1, A7 = 0 and `-IO/M`.
  - IC23 serves `0x80-0x1FF` in 32-byte blocks: G1 = A7, select = A5, A6 and A8, enabled by `-IO/M`.
- **[documented]** Selects, by port:

  | Port | Select | Device |
  |---|---|---|
  | `0x00` | `-FDC` | uPD72066 floppy controller |
  | `0x08` | `-DSK` | media control latch |
  | `0x10-0x38` | `-TMR0`..`-TMR5` | three 8254 and three 8253 timers |
  | `0x40` | `-DH` | not identified |
  | `0x48` | `-LCD` | LCD controller |
  | `0x50` | `-URTM` | HD63B50 ACIA (MIDI) |
  | `0x58` | `-HDCS` | hard-disk / SCSI option |
  | `0x60` | `-PANEL` | panel uPD71055 PPI |
  | `0x68` | `-GP` | data dial |
  | `0x70` | none | unused |
  | `0x78` | `-ENVDAC` | IC25 74HC259 envelope latch, voice chosen by A8-A10 |
  | `0x80`, `0xA0`, `0xC0` | `-DMA0`, `-DMA1`, `-DMA2` | the three uPD71071 |
  | `0xE0` | IC23 Y3 | uPD71059 interrupt controller (label unclear in the scan) |
  | `0x180` | `-ADC` | ADC |
  | `0x1A0` | `-DATCS` | digital audio interface |
  | `0x1C0` | `-MAP` | bank registers |
  | `0x1E0` | none | unused |

  Every select agrees with MAME's `io_map` and `common_map`.
- **[documented]** The interrupt controller takes D0-D7 on even bytes and uses CPU A1 as its register select, matching MAME's `umask16(0x00ff)`.
- **[static]** In both S950 ROMs 1.0a and 1.2b, `MOV DX,imm16` byte sequences load `0x01C0`, `0x01C2`, `0x01C4` and `0x01C6` (2, 3, 12 and 7 times), as well as `0x0180` and `0x01A0`. This is a byte-pattern count over the linear image, not a decoded listing, but it fits OS code writing the four bank registers.
- **[open]** The interrupt inputs IR0-IR7 of IC6 and their sources, and the meaning of `-DH` at `0x40`.

## Evidence

- **Documented.** Read from Akai's S950 CPU-board schematics, sheets 1/2 and 2/2 (PDF pages 6 and 8 of the scan hosted on s950fx.com). They were rendered at 600 dpi and read chip by chip on 2026-11-13. The scan is low resolution: the IC23 Y3 label could not be read, so that select is identified by where it goes (IC6 CS) instead. Every device select was compared with MAME's maps at the commit named above.
- **Static.** Byte-pattern count over the 1.0a and 1.2b linear images, 2026-11-13.
- Nothing here was checked on a machine.

## Open questions

- [Akai S950: the first things to establish](../questions/first-steps.md)
