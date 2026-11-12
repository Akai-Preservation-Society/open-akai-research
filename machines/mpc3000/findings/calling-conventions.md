---
id: mpc3000.calling-conventions
title: Calling conventions used by the OS, kernel and BIOS
machine: mpc3000
area: os
firmware: ["mpc3000-vailixi-3.50"]
status: static
hardware_tested: no
summary: OS application code is far cdecl (arguments pushed right to left, first argument at [BP+6], caller cleans up, RETF). The AMX kernel and the BIOS each use a different convention.
contributors: ["open-akai-research"]
last_verified: 2026-09-21
depends_on: ["mpc3000.address-model"]
---

# Calling conventions used by the OS, kernel and BIOS

Established on the Vailixi 3.50 reference image. The stock images very
likely share it (the startup-file loader has the same shape in all four),
but that has not been checked routine by routine: see the open question.

## Claims

- **[static]** Application code is **far cdecl**. The caller pushes arguments right to left, makes a far call, then removes the arguments with `ADD SP, n`. The callee opens with `PUSH BP / MOV BP, SP`, finds its first word argument at `[BP+6]` (a far pointer argument occupies `[BP+6]` offset and `[BP+8]` segment), and returns with `LEAVE / RETF` or `POP BP / RETF`.
- **[static]** Smallest specimen, `B060:0000` (linear `0x30600`, 13 bytes): it loads `CX` from `[BP+6]`, far-calls the kernel at `FB00:0484`, and returns with `RETF`. One caller pushes `14h`, calls it, and adds 2 to `SP`.
- **[static]** Argument order specimen: a caller pushes a word, then `DS`, then an offset, far-calls, and adds 6 to `SP`; the callee reads the far pointer with `LDS SI, [BP+6]` and the word from `[BP+0Ah]`.
- **[static]** Supporting counts over the whole image: `MOV AX, [BP+4]` (the first-argument form of near C code) never occurs; `MOV AX, [BP+6]` occurs 164 times; the byte pair `LEAVE, RETF` occurs 1,194 times, 1,169 of them inside linear `0x30000-0x6FFFF`, and never in the BIOS or kernel.
- **[static]** The **AMX kernel** (`FB00:`) is entered by far call with arguments in registers (the task or vector number in `DL`, a count in `CX`) and returns with `RETF`.
- **[static]** The **BIOS** (`F800:`) uses near calls internally, an inline-string routine that prints the text following the call, and software interrupts with the function number in `AX` ([bios-services.md](bios-services.md)).
- **[static]** The initialised-data segment is copied from linear `0x20000` to RAM segment `8010` at boot (31,890 bytes). A data offset `X` in that segment is therefore linear `0x20000 + X` in the image. Uninitialised data follows it in RAM (`8010:7C92` upward) and is zeroed at boot.
- **[hypothesis]** Far calls outnumber near calls across the OS. Raw opcode counts suggest it, but opcode bytes also occur inside data, so the counts are not instruction counts.
- **[open]** Whether callee-cleanup (`RETF n`) routines exist in meaningful numbers, how structures are packed, and whether any routine takes hidden arguments in `ES`.

## Evidence

- Static decoding of `mpc3000-vailixi-3.50` (2026-09-21): the specimens were decoded instruction by instruction; the counts are byte-pattern counts over the linear image. The `LEAVE, RETF` counts were recomputed on 2026-11-13.
- The specimen routine and the initialised-data image are pinned in [../pins/mpc3000-vailixi-3.50.csv](../pins/mpc3000-vailixi-3.50.csv).

## Open questions

- [A code map for the stock OS images](../questions/stock-os-code-map.md)
