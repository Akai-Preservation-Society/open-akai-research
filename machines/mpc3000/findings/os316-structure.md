---
id: mpc3000.os316-structure
title: OS 3.16 (M3K316.SYS) structure, memory and named routines
machine: mpc3000
area: os
firmware: ["mpc3000-v3.16-sys"]
status: static
hardware_tested: partial
summary: OS 3.16 is a self-contained MZ program with its own BIOS and AMX kernel. This gives its layout, address forms, start-up, tasks, memory use and a map of 111 named routines and data objects.
contributors: ["open-akai-research"]
last_verified: 2026-11-13
sources: ["M3K316.pdf release notes for OS 3.16 (2005)"]
depends_on: ["mpc3000.floppy-sys-loader", "mpc3000.address-model", "mpc3000.calling-conventions"]
---

# OS 3.16 (M3K316.SYS) structure, memory and named routines

OS 3.16 is the natural base for features delivered on floppy: every
examined EPROM OS loads it, and it does not depend on the EPROM after
start-up. Named addresses are in
[../symbols/mpc3000-v3.16-sys.csv](../symbols/mpc3000-v3.16-sys.csv);
pins are in [../pins/mpc3000-v3.16-sys.csv](../pins/mpc3000-v3.16-sys.csv).
Two defects in the stock file are in [os316-defects.md](os316-defects.md),
and how to add code to it is in [os316-extending.md](os316-extending.md).

## Address forms for this image

| Form | Meaning |
|---|---|
| Relative `seg:off` | As stored in the file, before relocation. **The form used in this section and in the symbol table** |
| Image offset | `seg × 16 + off`, a position in the load image |
| File offset | Image offset + `7A00h` (the header). **The form used by pins and `oar.py verify`** |
| Run-time logical | `L × 16` + image offset, where `L` is the load segment (`6900h` on 3.12 and Vailixi 3.50, `7000h` on 3.08 and 3.11) |
| Run-time physical | `0x300000` + logical (3.16 keeps the loader's third page table) |

Never use a 3.16 address with an EPROM image's offsets, or the reverse.

## Claims

### The file

- **[static]** `M3K316.SYS` is 458,047 bytes. MZ header: `7A0h` paragraphs (`7A00h` bytes); load image `6833Fh` bytes; 6,998 relocations starting at file offset `3Eh`; entry `0000:0000`; stack `7066:0100`; `e_minalloc` `15C7h` paragraphs.
- **[static]** The relocation table leaves room for 794 more entries before the end of the header.
- **[static]** The highest relocated segment value is `7DFAh`. Image, uninitialised data and stack end at relative paragraph `7DFBh`, so at run time 3.16 occupies logical `L × 16` to `L × 16 + 7DFB0h`.
- **[static]** The most-referenced segments are `0427h` (1,336 relocations: the LCD text routines), `609Ch` (688: the data segment), `05C8h`, `02D7h` (the field editor), `539Dh` (the Sound segment) and `0009h` (3.16's own BIOS).

### Start-up

- **[static]** The entry `0000:0000` is a C start-up. It sets `SS:SP = 7066:0100` and `DS = ES = 609Ch` (the data segment, DGROUP), zeroes the uninitialised data `DGROUP:7980h-FC9Eh`, calls the three initialisers listed at `6098:0004`, enables interrupts and jumps to `0281:0034`, the main loop.
- **[static]** DGROUP's initialised part ends exactly at the end of the load image (`609C0h + 7980h = 68340h`).
- **[static]** Initialiser 0 is `0009:0006`, 3.16's own BIOS (its banner is `MPC-3000 BIOS 02/20/05`). It programs the timer and the interrupt controller and installs its own `INT 41h`, `42h`, `43h`, `45h` and `46h` handlers in segment `0009`.
- **[static]** 3.16 links its own copy of the AMX kernel (segment `47BFh`, KADAK copyright at image `47BF9h`) and makes no genuine far call or jump into the EPROM's BIOS or kernel. After start-up, the EPROM matters only for having loaded the file.
- **[static]** 3.16 never writes the page registers (there is no `MOV DX,0FF00h`) and contains no `BRKXA`/`RETXA` (`0F E0` and `0F F0` do not occur in the image). It runs under the third page table the loader left: logical `00000h-F3FFFh` is RAM, `F4000h-F7FFFh` NVRAM, `F8000h-FFFFFh` the EPROM's BIOS range.
- **[hardware]** Stock `M3K316.SYS` loads and runs on a physical MPC3000 whose EPROM OS reports 3.50; its own `Searching floppy for startup files...` message appears after the hand-off.

### Tasks and interrupts

- **[static]** The AMX create table at image `4834Ch` holds eight 18-byte task records and ends with `FFFFh` at `483DCh`:

  | Task | Entry | Notes |
  |---|---|---|
  | 0 | `47BF:05AC` | kernel |
  | 1 | `04CD:000A` | |
  | 2 | `422F:000F` | playback tick |
  | 3 | `40FF:0005` | |
  | 4 | `3416:000A` | |
  | 5 | `03C1:000C` | |
  | 6 | `2FE8:0007` | |
  | 7 | `0281:0034` | user interface; stack `73E1:3E80` (16,000 bytes) |

- **[static]** 3.16 installs hardware-interrupt handlers through its kernel (`47BF:0341`, same interface as the EPROM kernel: vector in `DL`, handler in `ES:BX`): vector `08h` → `2B50:000C`, `09h` → `2C45:000C`, `0Ch` → `2C08:000E`, `0Dh` → `2B6D:006B`, `0Eh` → `2C1F:0000`. It also writes vectors `40h` and `09h` directly (image `2A645h`, `2CE57h`).
- **[static]** The AMX kernel at `47BF:0000-075B` leaves only by `RETF` or `IRET` to saved contexts: it has no far call, far jump, indirect transfer or `INT`.
- **[hypothesis]** Task 2's entry is the playback tick, because the live MIDI-in reader and the pad-event reader are both called from code in its segment. The other tasks' roles are not established.

### Memory

- **[static]** The sequence pool is fixed, not sized from free RAM: start-up code at image `48526h` computes the bound from two relocated constants (`MOV AX,7DFAh`, `SUB AX,7DF9h`, always 1), giving a pool from `0200:0000` to `6FFF:000E`, logical `2000h-6FFFEh`, whatever `L` is. With `L = 6900h` that overlaps 3.16's own code: see [os316-defects.md](os316-defects.md).
- **[static]** The Sound segment is `539Dh`: a working buffer at offset `0000` and Sound records from `4800h`, 24h bytes each.
- **[static]** The graphics framebuffer is `DGROUP:1579h`, 64 rows of 30 bytes (240 × 64 pixels), sent to the LCD by `1650:0F01`.
- **[emulator]** A waveform drawn into that framebuffer and blitted matched a 240 × 64 reference image pixel for pixel in MAME on all four EPROM sets.
- **[static]** Default pad notes: a 64-byte table at `DGROUP:087Fh` (image `6123Fh`), copied at start-up to `DGROUP:8064h`, which the pad code reads. Pad 1 is note 37, pad 2 note 36; the table is not in ascending order.
- **[hardware]** On a physical unit running 3.16, pad 2 showed `Note:36`.

### What 3.16 shares with the EPROM OS

- **[static]** Much of 3.16's application code is the same as the EPROM operating systems', relocated. Of the 111 symbols in the table, most were located by matching byte windows against named routines in `mpc3000-vailixi-3.50` (each row says how many opening bytes are identical), and their meanings were taken from what those routines were shown to do there.
- **[static]** The Edit Sound page has the soft keys `<Ply/Stp> <Best st> <Play X> <Do>` and eight `Do:` operations (COPY ZONE-> TEMP, INS TMP-> ZON ST, INS TMP-> ZN END, DELETE ZONE, DEL BEFR SOFT ST, DEL AFTR SFT END, SILENCE ZONE, REVERSE ZONE) dispatched through a jump table at `0B72:0B12` indexed 0-7.
- **[hypothesis]** Routines whose meaning was carried over from the EPROM OS behave the same in 3.16. The byte matches make this likely; only those exercised by the emulator test suites described in [os316-extending.md](os316-extending.md) have been seen to.
- **[open]** Large parts of 3.16 have no name here: the sequencer's data structures, MIDI file and sample-dump code, most of the disk and SCSI code, the Mixer, and the roles of tasks 1 and 3-6.

## Evidence

- **Static.** The header, relocation statistics, start-up path, tasks, vector installs, pool bound and absence of page-register writes were decoded from the file (2026-10-05 to 2026-10-17) and re-checked against its bytes on 2026-11-13. The symbol table's `notes` column records, for each routine mapped from the Vailixi 3.50 reference image, how many of its first 32 bytes are identical in 3.16; rows below 8 matching bytes were mapped with relocated segment words masked. Header, relocation table, task table, pad table and the opening bytes of every routine are pinned.
- **Emulator.** MAME `mpc3000`, 3.16 loaded on the `default` (3.12), `vailixi`, `v311` and `v308` sets, one execution each (2026-10-05 onward).
- **Hardware.** 2026-10-06, one physical MPC3000 with a Vailixi 3.50 EPROM, through a floppy-drive emulator: stock 3.16 and a modified 3.16 loaded; the modified build displayed the pad note. Photographs kept by the contributor. Not run on 3.08, 3.11 or 3.12 EPROMs.

## Open questions

- [Unmapped areas of OS 3.16](../questions/os316-unmapped.md)
- [Sequencer data model and timing](../questions/sequencer-model.md)
- [MIDI handling](../questions/midi-handling.md)
