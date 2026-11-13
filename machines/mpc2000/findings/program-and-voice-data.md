---
id: mpc2000.program-and-voice-data
title: Programs, note records, sequences, voices and the pitch table in OS 1.72 RAM
machine: mpc2000
area: os
firmware: ["mpc2000-v1.72-sys", "mpc2000-v1.72-exe"]
status: static
hardware_tested: no
summary: In OS 1.72 a program is a 30-byte header plus 64 note records of 29 bytes in an arena at segment 5A00; a 481-word pitch table is centred on 491A:07F8. Field meanings and the sequence layout are from a mod source, untested here.
contributors: ["open-akai-research"]
last_verified: 2026-11-13
sources: ["vubeatz (Dariusz Chynek), mpc2000_2000xl_mod_pack at commit eb8ece6, mods/*.S (PolyForm Noncommercial 1.0.0; facts restated, no code copied)"]
depends_on: ["mpc2000.os-files"]
---

# Programs, note records, sequences, voices and the pitch table in OS 1.72 RAM

These are in-memory layouts, not file formats. For the 2000XL's PGM file,
see [../../mpc2000xl/findings/file-formats.md](../../mpc2000xl/findings/file-formats.md);
nothing there is assumed to hold here.

## Claims

### Programs

- **[static]** The 24 programs live in an arena at segment `5A00`. The value `5A00h` appears as an immediate at EXE `0000:3752`, `0FE8:982E`, `0FE8:9C6E` and `0FE8:9D24`.
- **[static]** `1F31:2061` (EXE) is a 32-byte empty-program template: word `2`, the name `(Unused)` padded with spaces, then `.PRG`.
- **[documented]** `0FE8:97E6` (EXE, far) writes the 24 empty program records and the sequence terminator into the arena; it expects DS = `1F31`.
- **[static]** `0000:A610` (EXE) converts a note number to a note record by subtracting 35 and multiplying by 29 (`1Dh`).
- **[documented]** A program is a 30-byte header followed by 64 note records of 29 bytes for notes 35-98. A header word +0 of 2 or less marks an empty or deleted program. Header +1Dh holds 35 in stock programs (the mod reuses it for transpose).
- **[documented]** Note record (29 bytes):

  | Offset | Field |
  |---|---|
  | `+00h` | Far pointer to the sound |
  | `+05h` | Mode: 0 NORMAL, 1 SIMULT, 2 VEL SW, 3 DCY SW |
  | `+0Ah` | Voice overlap, 0-2 |
  | `+0Dh` | Tune word, -360..+360 tenths of a semitone |
  | `+0Fh` | Attack, 0-100 |
  | `+10h` | Decay, 0-100 |
  | `+11h` | Decay mode, 0-1 |
  | `+12h` | Filter frequency, 0-100 |
  | `+13h` | Resonance, 0-15 |

- **[documented]** Program slots: 24 far pointers at SYS `491A:9CB2`; current program far pointer at `491A:9D12`; selected program (0-based) at `491A:9D70`; pointer to the effective pad-to-note map (program or MASTER, 16 notes per bank x 4 banks, 34 = OFF) at `491A:9D16`.

### Pitch

- **[static]** SYS file `0x1BFB8`-`0x1C379` (`491A:0578`-`0939`) is a table of 481 strictly increasing words: `0400h` at the start, `1000h` at `491A:07F8`, `4000h` at the end, and `2000h` 120 entries above the centre. It reads as a playback-rate table indexed by pitch in tenths of a semitone (-240..+240) with `1000h` = unity. The table is pinned.
- **[documented]** OS code indexes it as word `[SI x 2 + 07F8h]` with SI = pitch in tenths. For tune values beyond +/-240 the mod halves or doubles the result. The stock path clamps tune to +/-360.

### Sounds and sample memory

- **[documented]** Sound record: +0 16-byte name; +1Ch dword length in PCM words; +30h pool handle. Stereo data uses a stride of (length + 15) rounded down to a multiple of 16.
- **[documented]** Sample memory pool: 130 entries of 10 bytes at `491A:5184` (base dword, length dword, next word), head index at `491A:56A2`. Valid PCM word addresses are below `01000000h`.

### Voices

- **[documented]** 32 voices. Voice table at `491A:9A6E`, 32 x 18 bytes (+0 note, +1 state). 32 voice-active words at `491A:570E`.

### Sequences

- **[documented]** The current sequence segment is at EXE `1F31:1D0A`. A sequence starts with its size in paragraphs (word +0), its number 1-99 at +13h, 64 track bytes at +430h (low 5 bits MIDI channel, `20h` MIDI out on), 64 track bytes at +4F0h (bit 0 = track used), and events from +530h ending with `FFh`.
- **[documented]** An event is 6 bytes: track (0-63); a word with the tick (up to `7FFh`) in bits 0-10 and duration bits 8-12 in bits 11-15; duration low byte; note (bit 7 = duration bit 13); velocity. Durations run 1-9999 ticks.
- **[documented]** UI state in EXE `1F31`: sequence index (0-based) at `0B20`, selected track at `0B21`.

## Evidence

- Static, 2026-11-13: the arena immediates, empty-program template, x29 arithmetic and pitch table were read from the two files at the offsets in [../symbols/](../symbols/) and pinned. The pitch table's shape was checked by script: monotonic, with the values given at index 0, 240, 360 and 480.
- Documented: all field meanings, record sizes other than 29, and the sequence layout come from the vubeatz mod source, which writes and reads these structures in its own code. Nothing was run here.

## Open questions

- [How OS 1.72 is loaded and where it runs](../questions/os-load-path.md)
