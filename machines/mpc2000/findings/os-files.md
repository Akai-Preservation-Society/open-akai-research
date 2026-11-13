---
id: mpc2000.os-files
title: OS 1.72 is two MZ files, and how a runtime address maps to a file offset
machine: mpc2000
area: firmware
firmware: ["mpc2000-v1.72-sys", "mpc2000-v1.72-exe"]
status: static
hardware_tested: no
summary: OS 1.72 is MPC2000.EXE (MZ header 0xE00) and MPC2000.SYS (MZ header 0x2800). EXE code segments 0000 and 0FE8 and data 1F31, and SYS segments 3000-based, convert to file offsets by fixed formulas checked against the bytes.
contributors: ["open-akai-research"]
last_verified: 2026-11-13
sources: ["vubeatz (Dariusz Chynek), mpc2000_2000xl_mod_pack at commit eb8ece6, mods/*.S (PolyForm Noncommercial 1.0.0; facts restated, no code copied)", "Sweetwater SweetCare: MPC2000 Operating System Update Instructions"]
---

# OS 1.72 is two MZ files, and how a runtime address maps to a file offset

Read this before using any address in this folder. It says which file an
address belongs to and how to find it in your copy of that file.

## Claims

- **[static]** OS 1.72 consists of two DOS MZ executables: `MPC2000.EXE` (196,404 bytes, header `0xE00` bytes) and `MPC2000.SYS` (133,932 bytes, header `0x2800` bytes, initial CS:IP `0000:0010`). Hashes are in [../firmware.toml](../firmware.toml). Each is its own firmware id, and file offsets in [../symbols/](../symbols/) and [../pins/](../pins/) are offsets into that file, header included.
- **[static]** `MPC2000.EXE` holds the text `MPC2000 Ver 1.72` and the date `May 14,1999` at file `0x20B7D`, and names both `MPC2000.EXE` and `MPC2000.SYS` (file `0x10739`, `0x107D5`). `MPC2000.SYS` ends with the text `1.72` at file `0x20B1D`.
- **[documented]** At run time the SYS image is loaded at segment `3000` and entered at `3000:0010`. Its MZ-relative segments `0000`, `0B7C`, `191A` and `23B0` therefore appear as `3000`, `3B7C`, `491A` and `53B0`.
- **[static]** SYS conversion: file offset = `0x2800 + (seg - 3000h) x 16 + off` for a loaded address, or `0x2800 + seg x 16 + off` for an MZ-relative one. With it, each of the 27 SYS code addresses in [../symbols/mpc2000-v1.72-sys.csv](../symbols/mpc2000-v1.72-sys.csv) lands on a routine prologue or on the instruction the source describes. The SYS data segment `491A` holds a 481-word pitch table centred on `491A:07F8` = `1000h` (see [program-and-voice-data.md](program-and-voice-data.md)), and `enter_params` at `3000:5B40` loads DS with the MZ-relative `191A`.
- **[documented]** The EXE's main code segment is `0000`, its second code segment `0FE8` ("aux") and its data segment `1F31`. The mod source also derives the main segment at run time from the INT 2Fh vector segment minus `0FE8`. So "segment 0000" is a load-relative value, not proof that the EXE sits at linear 0.
- **[static]** EXE conversion: file offset = `0xE00 + seg x 16 + off` (main: file - `0xE00`; aux: file - `0x10C80`). Checks: `0000:046B`, `0000:0626` and `0FE8:0359` are each a single `RETF`. `1F31:2061` is the 32-byte empty program record (word 2, `(Unused)`, `.PRG`). `0000:A610` computes the note-record offset as (note - 35) x 29.
- **[documented]** Calls from added code into EXE near routines go through a RETF gate: push a return frame, the gate address and the target, then RETF. The native dispatcher uses RETF when a callback's CS differs from the main CS.
- **[hypothesis]** The EXE is the loader and main program, and it reads `MPC2000.SYS` from the boot disk. Supported by the two file names inside the EXE and the mod source's description, but no loader code has been traced here.
- **[open]** How the EXE itself is loaded and started, where in physical memory it sits, and the hardware memory map. See [../questions/first-steps.md](../questions/first-steps.md) and [../questions/os-load-path.md](../questions/os-load-path.md).

## Evidence

- Static, 2026-11-13: MZ header fields and version strings read from the two files (hashes in firmware.toml) and pinned in [../pins/](../pins/). Each symbol was located with the formulas above and disassembled with `ndisasm -b16` at its file offset. Code entries were accepted when the byte before is a return or padding and the first instructions are a prologue (`PUSH BP; MOV BP,SP` or `ENTER`), or are the instruction the source names. Every listed address passed. The first 16 bytes of each code symbol are pinned.
- Documented: the load segment, segment roles and RETF-gate convention come from comments and constants in the vubeatz mod source. That source states its package was not assembled or tested, although some comments describe earlier hardware use.
- The OS update format (two files on a DOS floppy) is from Sweetwater's update instructions.

## Open questions

- [How OS 1.72 is loaded and where it runs](../questions/os-load-path.md)
- [Akai MPC2000: the first things to establish](../questions/first-steps.md)
