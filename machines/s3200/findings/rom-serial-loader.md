---
id: s3200.rom-serial-loader
title: The second ROM entry DFE8:00D1, a serial byte loader
machine: s3200
area: boot
firmware: ["s3200-v2.00"]
status: static
hardware_tested: no
summary: ROM entry DFE8:00D1 (file 0x1FF51) receives two count-prefixed blocks on the serial unit at 0xC020, echoing each byte, into logical 0x00000-0x1FFFF, then jumps to 0000:0000. No caller of its only jump (0x192C6) is known. Its purpose is not established.
contributors: ["open-akai-research"]
last_verified: 2026-11-02
depends_on: ["s3200.address-model", "s3200.peripherals"]
---

# The second ROM entry DFE8:00D1, a serial byte loader

A small routine in the boot block that can load code over the serial
port. Not a usable route today: nothing is known to reach it.

## Claims

- **[static]** File `0x3FFF5` holds `JMP FAR DFE8:00D1` (physical `0xDFF51`, file `0x1FF51`), reached as `FFFF:0005`.
- **[static]** Inputs: AL selects a divisor (`2/AL` is written to timer counter 1 at `0xC032`; AL = 0 causes a divide error at `0x1FF59`), BX seeds a blink counter, and DX is an indicator port used only if `[0000:7F61]` is non-zero (otherwise port `0x54`).
- **[static]** It disables interrupts, sets SS=`0x3000`, SP=0 and DS=ES=0, and blinks the indicator while polling `0xC022` bit 1. Then, twice, it reads a 16-bit little-endian count and that many bytes (count 0 means 65,536), storing them from `0000:0000` and then from `1000:0000`, and writes NOT BH to port `0x54` per byte. Each byte is read from `0xC020` after `0xC022` bit 1, and written back to `0xC020` after `0xC022` bit 0 (echo). It then jumps to `0000:0000` at `0x1FF4C`.
- **[static]** Every branch target lies in `0x1FF4C-0x1FFD5`, so it exits only through that jump or the divide error. It replaces only logical `0x00000-0x1FFFF`; `0x20000-0x3FFFF`, which holds segment `2033`, is untouched.
- **[emulator]** One run of the routine alone in a purpose-built tracer (AL=1, DX=`0x1234`, `[7F61]`=0, input `03 00 11 22 33 02 00 AA BB`) took 223 steps. It wrote counter 1, blinked port `0x54`, echoed all 9 bytes each before the next read, stored the data at the two addresses and reached `0000:0000`.
- **[static]** The only transfer to `FFFF:0005` in the image is `MOV BL,[0x7551]; JMP FAR FFFF:0005` at `0x192C6` (`0FE9:9436`). The byte before it is a `RET`. A whole-image search found no near or short jump, far pointer, `PUSH` immediate or table word reaching `0x192C6`. It is reached only by a computed jump or not at all.
- **[static]** After the boot block, the page registers map logical `0xC0000-0xFFFFF` to RAM at physical `0x1C0000-0x1FFFFF`, the OS never changes them, and the OS uses segments `C000-E000` as RAM (for example at `0x23ED4`). So a jump to `FFFF:0005` from the running OS lands in RAM, not in this ROM routine, unless XAM is off.
- **[open]** Who calls it, what it is for (factory test, service download or OS update), and which connector carries the serial lines (MAME says the V53 serial unit is MIDI).

## Evidence

- Static: `ndisasm -b16 -o 0xD1` of `0x1FF51-0x1FFD5` and of the jump at `0x192C6`; whole-image byte searches for `EA`/`9A` with `05 00 FF FF` and `D1 00 E8 DF`, and a rel8/rel16, word and far-pointer scan for `0FE9:9436`; by the contributor 2026-11-01 and 2026-11-02. Pins: `0x1FF51` (133), `0x1FF4C` (5), `0x192C6` (9), `0x3FFF0` (10), `0x23ED4` (16).
- Emulator: the contributor's own unpublished purpose-built 8086 tracer of this routine alone, with scripted serial input and a pre-registered expected result, 2026-11-01. It does not show that any OS path reaches the routine.

## Open questions

- [Purpose and caller of the ROM serial loader](../questions/rom-serial-loader.md)
