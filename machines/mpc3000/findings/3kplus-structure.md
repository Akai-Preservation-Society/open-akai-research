---
id: mpc3000.3kplus-structure
title: 3K PLUS 1.0 is OS 3.16 plus an appended code segment, and how it starts and hooks 3.16
machine: mpc3000
area: os
firmware: ["mpc3000-3kplus-1.0-sys", "mpc3000-v3.16-sys"]
status: static
hardware_tested: no
summary: 3K PLUS 1.0 (STARTUP.SYS) is OS 3.16 with a 41,820-byte resident code segment (the cave) that runs at E700:0000 on every examined EPROM. 91 of 3.16's pins still match. RAM above the cave, logical F1370-F3FFF, is not referenced by its code.
contributors: ["open-akai-research"]
last_verified: 2026-11-16
sources: ["3K PLUS 1.0 README.txt (release folder, 2026)"]
depends_on: ["mpc3000.os316-structure", "mpc3000.os316-extending", "mpc3000.os316-defects", "mpc3000.floppy-sys-loader"]
---

# 3K PLUS 1.0 is OS 3.16 plus an appended code segment

How 3K PLUS is put together, which OS 3.16 addresses still hold in it, where its
own code lives at run time, and which RAM is left for further additions.

## Address forms

As for OS 3.16 ([os316-structure.md](os316-structure.md)): relative `seg:off`,
image offset = `seg × 16 + off`, **file offset = image offset + `7A00h`** (used by
pins). The cave is staged at relative paragraph `6834h` and runs at relative
paragraph `7E00h`; it is assembled at offset 0, so **cave offset `x` = relative
`7E00:x` = image `68340h + x` = file `6FD40h + x`**. At run time the load segment is
always `6900h` (see below), so `7E00:x` runs at segment `E700h`, logical `E7000h + x`,
physical `0x3E7000 + x` (OS 3.16 keeps the loader's third page table).

## Claims

### Identity and relation to OS 3.16

- **[documented]** The release README calls it "Akai's OS 3.16 maintenance upgrade with new features added", loaded from floppy as `STARTUP.SYS`, for 3.08, 3.11, 3.12 and Vailixi 3.50 EPROMs; tested by its author on one Vailixi 3.50 machine and in emulation. It lists waveform view, zones, Lazy Chop with `<To program>`, Compress sound, Input Thru, mute groups, Apply To, Track Mute, more Timing Correct values, sync to all outputs, screen mirror over MIDI, MIDI Remote and disk tools. It says PGM and APS files saved by 3K PLUS carry mute groups that stock 3.16, 3.08, 3.12 and Vailixi 3.50 ignore, and that sound memory is 16K smaller (Input Thru). No licence is stated.
- **[static]** MZ header: header `7A0h` paragraphs, stack `7066:0100` (both as 3.16), 7,439 relocations (3.16: 6,998), load image `74646h` bytes, entry `6834:A35B`. The header still has room for 353 more relocations.
- **[static]** 95 of the 109 byte ranges pinned for `mpc3000-v3.16-sys` match. The 14 that do not are the whole image, the MZ header, the relocation table, DGROUP's initialised data and ten routine openings that 3K PLUS overwrote with far jumps into the cave (`lcd_put_char`, `lcd_restore_text`, `lcd_put_string`, `wave_transfer`, `sound_free`, `sound_find`, `dsp_channel_stop`, `scsi_partition_reader` (twice), `midi_buffer_send`). `note_on`, `song_page`, `program_record`, `program_select`, `track_slot_map`, `pgm_load` and `aps_load` are unchanged, unlike in [TME 3.41](tme341-structure.md). The 91 matching ranges that are not already covered here are re-pinned for this id.
- **[static]** It is not built on TME 3.41: TME's pinned strings (`OS 3.41 Track Mute Edition`, `3.41 Hybrid Format`) and MZ header do not match, and the two routines TME changed (`song_page`, `note_on`) keep 3.16's bytes here.

### Start-up: one resident segment, always at E700h

- **[static]** The entry `7E00:A35B` copies `51AEh` words (**`A35Ch` bytes, cave `0000`-`A35B`**) from the staged copy to `L + 7E00h` and jumps to OS 3.16's entry. Cave `A35C`-`C305` (8,106 bytes: the entry code, a move routine and a relocation table) is used once and never copied. So the resident cave is 41,820 bytes, not the 49,926 the file appends.
- **[static]** The entry reads the load segment from a relocated `FFFFh` (`L − 1`). If `L > 6900h` (3.08, 3.11) it moves the whole image down to `6900h` using its own table at `7E00:A49C`, then re-enters itself. Parameters at `7E00:A496`: `7465h` paragraphs moved, `1D10h` table entries, minimum move `01FCh` paragraphs. The table decodes to exactly the 7,439 MZ relocations plus one 64 KiB skip marker.
- **[static]** Consequence: on every examined EPROM, OS 3.16 runs with `L = 6900h` and the cave at segment `E700h` (logical `E7000h`-`F135Bh`).
- **[static]** The entry applies the [sequence-pool fix](os316-defects.md) itself: if the immediate at `4853:0005` still holds `6FFFh` it is set to `L − 1 − 120h`.
- **[static]** The [SCSI stack fix](os316-defects.md) is in place: `scsi_partition_reader` jumps to `7E00:47B4`, which runs the reader on a private stack of `1200h` bytes at segment `pool_end + 1`, refusing if that is above `L − 120h`. The stack lies below the OS code, not above the cave.
- **[emulator]** CPU-only check, not MAME: in Unicorn 2.1.4 (x86 16-bit real mode, ROM-loader model of [floppy-sys-loader.md](floppy-sys-loader.md): image at `L × 16`, relocations applied, `CS:IP`/`SS:SP` from the header, interrupts off), the start-up reaches `6900:0000` from both `L = 6900h` and `L = 7000h`, and writes nothing in logical `F135C`-`F3FFF` or at `F4000` and above.

### Hooks into OS 3.16

- **[static]** 3K PLUS changes 3.16 by far jumps and calls into the cave (`EA`/`9A` with relocated segment `7E00h`): 143 such sites in the 3.16 part. Pinned here: the eight routine openings above; `program_init` `207C:02D3` → `7E00:20FC` (clears the program's mute groups first); program copy `19F9` → `7E00:211D` (copies mute groups); and four `file_close` calls in PGM/APS load and save, replaced by calls to `7E00:2177`, `21AE`, `21F1`, `221B` ([3kplus-lazy-chop.md](3kplus-lazy-chop.md)).
- **[static]** `sound_free` (`21E7:0B1F`) → `7E00:1AD2`, which clears the zone state when the freed Sound is the zone source, then continues at `21E7:0B25`.

### RAM left for further code

- **[static]** No cave instruction addresses its own segment at or above `A35C`: the highest direct variable is `7E00:A35A`; of the 162 relocated `7E00h` words, every far call, far jump and stored far pointer targets an offset below `A347` (the remaining one is the entry code's own segment load at `7E00:A369`); no unrelocated value in `E700h`-`F3FFh` is loaded into a segment register anywhere in the image; the only `CS`-relative segment arithmetic is the SCSI wrapper's `CS + 8200h` (= `L`).
- **[static]** One exception bounds the free area from below: the MIDI Remote handler sets bits in a table at `7E00:A34C` indexed by `(byte − 40h) >> 3` with only a lower-bound check (`7E00:A216`-`A27B`). A byte `80h`-`FFh` reaching it would write up to `7E00:A363`.
- **[hypothesis]** Only MIDI data bytes (below `80h`) reach that path, so the table stays inside `A34C`-`A353`. Not established: depends on what OS 3.16's SysEx state passes on.
- **[static]** Usable RAM for added code is therefore logical **`F1370`-`F3FFF`** (cave offsets `A370`-`CFFF`, 11,408 bytes), keeping `A35C`-`A36F` as a guard. `F4000` is the NVRAM window (page 61).
- **[open]** Whether anything writes `F135C`-`F3FFF` at run time (pointer writes, DMA). See the question below.

## Evidence

- **Documented:** the README.txt shipped in the 3K PLUS 1.0 release folder (also in a "1-2.0" folder with an identical `STARTUP.SYS`).
- **Static:** decoded from the file whose hash is `mpc3000-3kplus-1.0-sys`, 2026-11-15/16, with LLDB's 16-bit x86 decoder (`i386-unknown-unknown-code16`), following control flow from the MZ entry and from every relocated `7E00h` reference; pin comparison with `python3 tools/oar.py verify mpc3000-v3.16-sys STARTUP.SYS` (95 ok, 14 failed). Pinned ranges are in [../pins/mpc3000-3kplus-1.0-sys.csv](../pins/mpc3000-3kplus-1.0-sys.csv); `oar.py verify mpc3000-3kplus-1.0-sys` checks them.
- **Emulator:** Unicorn 2.1.4 CPU emulation, 2026-11-15, one run per load segment, comparing the original file with a modified one; write hooks on all memory. Not MAME, not a machine model.
- Nothing here has been run on hardware by this project.

## Open questions

- [Is RAM above the 3K PLUS cave free at run time?](../questions/3kplus-free-ram-at-runtime.md)
