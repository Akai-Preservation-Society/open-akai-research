---
id: mpc2000xl.os-services-from-mods
title: OS 1.20 routines, software interrupts and RAM structures used by the vubeatz mods
machine: mpc2000xl
area: os
firmware: ["mpc2000xl-os1.20"]
status: documented
hardware_tested: no
summary: About 20 far routines in OS 1.20 (screen, editor, voice stop, DSP transfer, sample memory), INT 7Fh-EAh services, the in-RAM program and sound records and a 481-word pitch table at 582B:0056. Entries checked against the bytes; meanings from a mod source.
contributors: ["open-akai-research"]
last_verified: 2026-11-13
sources: ["vubeatz (Dariusz Chynek), mpc2000_2000xl_mod_pack at commit eb8ece6, mods/*.S (PolyForm Noncommercial 1.0.0; facts restated, no code copied)"]
depends_on: ["mpc2000xl.address-model", "mpc2000xl.abi-and-hooks"]
---

# OS 1.20 routines, software interrupts and RAM structures used by the vubeatz mods

Adds to [abi-and-hooks.md](abi-and-hooks.md). The source is a mod pack
that calls these routines. Its own README says the package was not assembled or tested.
Names and addresses are in [../symbols/mpc2000xl-os1.20.csv](../symbols/mpc2000xl-os1.20.csv).

## Claims

- **[static]** Each code address below is a routine entry in OS 1.20 (`seg x 16 + off` = file offset; preceded by a return or padding; starts with a prologue). Exception: `bank_get` at `3E19:0752` sets up a frame and executes `INT 37h`. All of them except `35B0:00AC` and `35B0:0418` lie at or above file `0x38000`, so the remap rule in [address-model.md](address-model.md) applies to calls made from interrupt code.

### Routines

| Address | Name | Arguments and cleanup (per the source) |
|---|---|---|
| `3E19:0662` | `lcd_draw_resource` | push seg, off of a resource stream; caller pops 4 |
| `3E19:0724` | `register_event_table` | push seg, off; caller pops 4. Entries: key byte, off, seg |
| `3E19:0752` | `bank_get` | returns the pad bank in AX |
| `3E19:0988` | `draw_text_at` | push seg, off, y, x; caller pops 8 |
| `3E19:09EE` | `draw_signed_number` | push width, value dword, y, x; caller pops 10 |
| `3E19:9E5A` | `editor_refresh` | after an editor draw |
| `35B0:0418` | `program_pointer_by_index` | push `5Ch` + DRUM (0-3) for the program, `60h` + DRUM for the effective pad map; DX:AX; caller pops 2 |
| `35B0:62BE` | `numeric_editor_open` | push value pointer and descriptor; caller pops 8 |
| `35B0:00AC` | `div32` | 32-bit divide, DX:AX |
| `4E16:055A` / `0606` | `params_reenter` / `params_draw` | PARAMS page |
| `4E16:1F3A` / `2614` | filter / voice child windows | PARAMS sub-windows |
| `4E16:086C` | `audition_stop` | also disables the pad callback |
| `3E19:3A36` / `3A02` | `voice_stop` / `voice_quiet` | push voice; caller pops 2 |
| `3E19:0034` | `dsp_write` | count, buffer far, destination dword; caller pops 10 |
| `3E19:0066` | `dsp_read` | `1000h`, count, buffer far, source dword; caller pops 12 |
| `3E19:193E` / `1A18` | `sample_arena_top` / `sample_compact` | high-water mark in DX:AX / compact sample memory |

- **[documented]** Each routine above is described as the source uses it. None has been called by this project.
- **[documented]** Software interrupts, adding to the inline ones in [abi-and-hooks.md](abi-and-hooks.md): `INT 90h` text or number at CL = x, CH = y (BL = 5 text at DX:SI; BL = 8 number, BH = width); `INT 91h` ALL-file stream I/O (BL = 9 write CX bytes from ES:SI, BL = 6 read into ES:DI); `INT 96h`/`97h`/`98h` bind key-press, key-release and shifted callbacks; `INT 7Fh` numeric editor (AX value, BX min, DX max, DI store callback); `INT A4h` clear editors and callbacks; `INT C5h` the active track's DRUM/program in ES:SI; `INT C7h` 16 LEVELS set-up; `INT EAh` before ALL data is appended.
- **[documented]** `INT 96h` event codes: F1-F6 = `60h`, `66h`, `6Ch`, `72h`, `78h`, `7Eh`; MAIN `0Ch`; refresh `C0h`; idle `C6h`; decrease/increase `B4h`/`BAh`; cursor left/right/up/down `8Ah`/`90h`/`96h`/`9Ch`; AFTER `4Eh`; slider `D8h`.

### Data in segment 582B

- **[static]** File `0x58306`-`0x586C7` (`582B:0056`-`0417`) is 481 strictly increasing words: `0400h`, `2000h` at index 360, `4000h` at the end, and `1000h` at `582B:0236`. This is a pitch-to-rate table, indexed by pitch in tenths of a semitone from -240 to +240, with `1000h` as unity. It is pinned.
- **[documented]** The program in RAM is a 30-byte header and 64 note records of 24 bytes: +0 mode, +5 voice overlap, +8 tune word (-360..+360), +0Ah attack, +0Bh decay, +0Ch decay mode, +0Dh filter frequency, +0Eh resonance. Program +7DEh is a table of 64 far pointers to sound records. A header word +0 below `1Eh` marks an unused program. The +0 and +5 meanings agree with the 24-byte layer in the PGM file ([file-formats.md](file-formats.md)).
- **[documented]** Sounds: 256 records of 62 bytes at `582B:991A`, linked from a far head pointer at `582B:98DC` (+0 next pointer, +12h 16-byte name, +25h stereo flag, +2Eh length dword). Sample arena limit dword at `582B:8FC6`.
- **[documented]** Voices: 32 x 20 bytes at `582B:9609` (+0 DRUM, +1 note; `FFh` at `582B:960A` = voice 0 idle).
- **[documented]** UI: ASSIGN selector `582B:8D5E` indexing 42-byte descriptors at `582B:2C9C`; PARAMS selector `582B:8D66` (2-8); selected DRUM `582B:D7BE`; selected note `582B:D7C0`.
- **[documented]** DSP voice registers: `OUT 80h` with `voice | 0300h`, then `OUT 82h`, `84h`, `86h` with 0, forces a voice's envelope to zero. Native PCM transfers use DSP channel 0.

## Evidence

- Static, 2026-11-13: every code address was converted with `seg x 16 + off` and disassembled with `ndisasm -b16` in the image whose sha256 matches `mpc2000xl-os1.20`. The first 16 bytes of each are pinned. The pitch table was checked by script and pinned whole.
- Documented: meanings, arguments, structures and port use come from the vubeatz mod source. The source names its XL base only as "XL Update 1.3", not by OS version or hash. These addresses match stock OS 1.20 bytes, but the agreement is about entry points only.
- Not run on hardware or in an emulator by this project.

## Open questions

- [A map of the OS 1.20 code](../questions/os120-code-map.md)
- [The L6028 sample engine](../questions/sample-engine.md)
