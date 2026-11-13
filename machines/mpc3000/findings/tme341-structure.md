---
id: mpc3000.tme341-structure
title: OS 3.41 Track Mute Edition is built on OS 3.16
machine: mpc3000
area: os
firmware: ["mpc3000-tme-3.41-sys", "mpc3000-v3.16-sys"]
status: static
hardware_tested: no
summary: The OS 3.41 Track Mute Edition SYS file is OS 3.16 with changes. It has the same MZ layout, 95% of 3.16's load image is unchanged at the same offsets, and 103 of 108 pinned 3.16 ranges still match. A 3.16 address may be used for 3.41 only where a pin for it passes.
contributors: ["open-akai-research"]
last_verified: 2026-11-13
sources: ["MPC3000 OS 3.40.0 Track Mute Edition README (English, PDF, Deep88, November 2026)"]
depends_on: ["mpc3000.os316-structure"]
---

# OS 3.41 Track Mute Edition is built on OS 3.16

How much of the OS 3.16 map applies to Deep88's Track Mute Edition, and
how to check a given address before using it.

## Claims

- **[documented]** The Track Mute Edition is a free, closed-source, floppy-loaded OS by Deep88. Its README says it is "based on OS 3.12", that it was first tested in MAME's MPC3000 driver, and that there is no EPROM version. Features listed for 3.40.0 and 3.41 include a Track Mute page on SONG, Note Repeat on TIMING CORRECT, sampling while the sequencer runs, incremental chopping, a bit and sample-rate reducer, normalize, mute groups, Double STOP, a hybrid SCSI format, sample preview, automatic chopping of a take onto pads, and a MIDI "pad out" track mode. Its settings are kept in a SETUP file next to the usual PARAMS file.
- **[static]** The released file is named `M3K340.SYS`, but its strings say `System 3.41` (file `0x6955A`) and `OS 3.41 Track Mute Edition` (`0x8715D`). Strings for earlier builds remain (`OS 3.33`, `OS 3.36 TEST3`, `OS 3.37 GOLD`). The README tells users to copy `M3K341.SYS`. Identify the file by hash ([../firmware.toml](../firmware.toml)), not by name.
- **[static]** Its MZ header has the same layout as OS 3.16's ([os316-structure.md](os316-structure.md)): a `7A0h`-paragraph header, relocations from `3Eh`, entry `0000:0000`, stack `7066:0100`. It has 7,586 relocations against 3.16's 6,998; the 588 extra fit in the 794 spare slots 3.16's header leaves. The load image is `7FFE3h` bytes against `6833Fh`, and `e_minalloc` is 0 against `15C7h`.
- **[static]** It carries 3.16's own BIOS (banner `MPC-3000 BIOS 02/20/05` at `0x7BB1`, as in 3.16).
- **[static]** Compared with `mpc3000-v3.16-sys`, 405,749 of 426,815 bytes of 3.16's load image (95.06%) are identical at the same file offset. The differences fall in 91 regions; the largest are at image offsets `0x23558-0x2447E`, `0x24600-0x26281` and `0x266A0-0x28695`. A further 97,444 bytes follow the end of 3.16's image.
- **[static]** Of the 108 byte ranges pinned for 3.16, 103 still match in 3.41. The five that differ are the MZ header, the relocation table, the DGROUP initialised data, `song_page` (file `0x0E11A`) and `note_on` (`0x288DD`). The matching ranges are pinned again for this image in [../pins/mpc3000-tme-3.41-sys.csv](../pins/mpc3000-tme-3.41-sys.csv), so `oar.py verify mpc3000-tme-3.41-sys` checks them.
- **[hypothesis]** `song_page` and `note_on` were replaced or hooked for the Track Mute page, mute groups and the MIDI pad-out mode. Reason: these are the two code pins that changed, and those are the features that touch SONG and note playback. Not traced.
- **[open]** Whether the two memory defects of stock 3.16 ([os316-defects.md](os316-defects.md)) are still present in 3.41, and where the appended code and data sit at run time.

## Evidence

- Static, 2026-11-13: MZ header fields and strings read from the released `M3K340.SYS`. The load image was compared byte for byte with an `M3K316.SYS` whose hash equals `mpc3000-v3.16-sys`, with regions merged across gaps under 8 bytes. `python3 tools/oar.py verify mpc3000-v3.16-sys M3K340.SYS` gave 103 ok and 5 failed ranges.
- Documented: the author's English README (PDF) shipped with the release. The features are the author's description; none was tested here.
- Nothing here was run in an emulator or on hardware.

## Open questions

- [Unmapped areas of OS 3.16](../questions/os316-unmapped.md)
