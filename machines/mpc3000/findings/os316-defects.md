---
id: mpc3000.os316-defects
title: Two memory defects in stock OS 3.16, and their fixes
machine: mpc3000
area: os
firmware: ["mpc3000-v3.16-sys"]
status: emulator
hardware_tested: partial
summary: On 3.12 and Vailixi 3.50 EPROMs stock OS 3.16 lets sequence data overwrite its own code and hangs at Song. With a SCSI disk its partition reader wraps the stack. Both causes and working fixes are described.
contributors: ["open-akai-research"]
last_verified: 2026-10-17
depends_on: ["mpc3000.os316-structure"]
---

# Two memory defects in stock OS 3.16, and their fixes

Addresses are relative 3.16 `seg:off` and image offsets, as defined in
[os316-structure.md](os316-structure.md).

## Claims

### 1. The sequence pool overlaps the program (3.12 and Vailixi 3.50 EPROMs)

- **[static]** The sequence pool is fixed at logical `2000h-6FFFEh`. The pool end comes from the immediate of `MOV BX,6FFFh` at image `48535h`, read once after start-up by `4852:0006`.
- **[static]** With `L = 7000h` (3.08, 3.11) the pool ends just below the program. With `L = 6900h` (3.12, Vailixi 3.50) it covers logical `69000h-6FFFEh`, which is 3.16's own image offsets `0000h-6FFEh`: live code, including segment `0427h`, the most-used code segment. The pool reports this space as free (439K).
- **[emulator]** Stock `M3K316.SYS` on the 3.12 and Vailixi 3.50 sets hangs at the Song screen after a short recording. On the 3.08 and 3.11 sets the same steps work.
- **[static]** Fix: before 3.16 starts, set the immediate at image `48535h` to `L − 1`. The pool then ends at `L × 16 − 2`: unchanged on 3.08 and 3.11, 28K smaller on 3.12 and 3.50 (411K free). Every reader of the pool variables (`DGROUP:8B13h-8B19h`) uses the bound set from the immediate, so a sequence too big for the smaller pool is refused rather than written over code.
- **[emulator]** With the fix, the same recording followed by Song works on all four sets, no pool write reaches logical `69000h-6FFFFh`, and the program bytes stay unchanged.
- **[hardware]** A fixed build on a physical unit with a Vailixi 3.50 EPROM (`L = 6900h`) kept working with sequence memory filled to 0% free and refused further steps.
- **[open]** Whether stock 3.16 corrupts itself on real hardware with a 3.12 EPROM. It is expected from the addresses but has not been observed.

### 2. The SCSI partition reader wraps the stack

- **[static]** The SCSI partition reader `2AB2:04F7` (image `2B017h`) opens with `SUB SP,100Eh`: a 4 KB sector buffer plus locals.
- **[static]** The Disk page `077D:042D` opens a `3652h`-byte frame, the largest in 3.16. When it calls the media check, the reader is entered on the UI task's stack with `SP = 07D2h`, so `SP` wraps to `F7C2h`.
- **[emulator]** With a SCSI disk active, Disk mode makes the reader and its callees write at UI stack-segment offsets `F6xxh-FFFFh`, which is image `835xxh-83E0Fh`: above 3.16's extent (`7DFB0h`), in RAM that 3.16 does not otherwise use. Stock 3.16 does not visibly fail, but anything placed there (for example added code) is overwritten.
- **[static]** Fix used in practice: run the reader on a private stack. Lower the pool end by a further `120h` paragraphs (4,608 bytes; the pool then reports 407K), place the stack in the gap between pool and program, and hook the reader's prologue with a wrapper that switches `SS:SP`, runs the body from `2AB2:04FE`, and switches back.
- **[static]** That fix is safe because the kernel saves and restores `SS:SP` verbatim on interrupts and task switches, and the reader's whole call tree (857 instructions) loads neither `SS` nor `SP`.
- **[emulator]** The deepest stack use measured on the reader paths (boot scan, Disk page, Erase all on SCSI) is `109Ah` bytes, inside the `1200h` provided. With the fix no write lands above the program during those operations, and Disk mode lists and erases files normally, on all four EPROM sets.
- **[open]** Deeper interrupt nesting than the measured paths.

## Evidence

- **Static.** Decoded from `M3K316.SYS` (2026-10-05 and 2026-10-16); the pool immediate, its computation, the reader prologue and the Disk page prologue are pinned in [../pins/mpc3000-v3.16-sys.csv](../pins/mpc3000-v3.16-sys.csv). Stack use of the reader's call tree was established by a static walk of every instruction reachable from `2AB2:04FE`.
- **Emulator.** MAME `mpc3000`, the four EPROM sets, one execution per case, with write taps on the relevant ranges. Stock and fixed files were run on the same sequence of key presses.
- **Hardware.** 2026-10-06, one physical unit, Vailixi 3.50 EPROM, a 3.16 build carrying the pool fix. The SCSI fix came later; no hardware run of it is recorded here.

## Open questions

- [Unmapped areas of OS 3.16](../questions/os316-unmapped.md)
