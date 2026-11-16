---
id: mpc3000.3kplus-lazy-chop
title: How 3K PLUS 1.0 turns zones into a program (Lazy Chop "To program") and stores mute groups
machine: mpc3000
area: os
firmware: ["mpc3000-3kplus-1.0-sys"]
status: static
hardware_tested: no
summary: In 3K PLUS 1.0, <To program> makes one Sound per zone (checking records and memory first, freeing them again on failure), wipes and renames the chosen program, and puts zone i on pad slot i. Mute groups live in a cave table and are saved as a MUTEGP35 trailer after PGM/APS data.
contributors: ["open-akai-research"]
last_verified: 2026-11-16
sources: ["3K PLUS 1.0 README.txt (release folder, 2026)"]
depends_on: ["mpc3000.3kplus-structure", "mpc3000.program-records-and-pad-maps"]
---

# How 3K PLUS turns zones into a program

Addresses are cave offsets `7E00:x` (file `6FD40h + x`) unless written as an OS 3.16
`seg:off`; see [3kplus-structure.md](3kplus-structure.md). Record and pad-map
layouts are in [program-records-and-pad-maps.md](program-records-and-pad-maps.md).

## Claims

### The page

- **[documented]** Reached from Program/Sounds → 6 (Edit Sound) → HELP (waveform view), zones or Lazy chop, then soft key `<To program>`; the README says it turns the zones into Sounds on a new drum program with a mute group 1-4 or OFF.
- **[static]** Page entry `5B7C` (jumped to from `4F60`, `4F76`). Title `=========== Zones to Program ===========`. Fields: Program (`cs:6517`, 0-23) and Mute group (`cs:6518`, 0 = OFF, 1-4); cursor field in `cs:6519` (0 or 1). On entry the program defaults to the next program after the current one whose 64 entries are all empty (`5F4B`), and the mute group to 1.
- **[static]** The `Pads:` line shows `A01` to the slot of the last zone (`606E`-`608E`): zones always start at pad A01.
- **[static]** Do it (key code `78h`) is ignored until 100 ticks of `DS:D38C` have passed since the page or prompt was drawn (`5DAF` stamps the time and drops queued keys; `5DDA` tests it). `DS:D38C` is incremented by OS 3.16's vector-08h handler (`2B50:0028`); the tick length is not established. Then: `Stop the sequencer first` if the sequencer runs (`5CCA`), `Zone nn too short` below `558h` frames (`5DE6`), and, if the chosen program is not empty, `REPLACE PROGRAM nn?` with `<Replace>`/`<Cancel>` (`5CF6`-`5D5B`). Cancel shows `Program kept`.

### The executor (`615F`-`62EC`)

- **[static]** Order: make the Sounds (`1AED`, entered with `BP` loaded from `cs:7B7C`, the Edit Sound page's frame); copy the new Sound numbers to `cs:66A2`; wipe the program (`20FC` = 3K PLUS's wrapper of `program_init`, which also clears its mute groups); rename it (`5E36`, unique name with a numeric suffix); `program_select`; assign; enable the program's mute groups if a group was chosen (`206A`); show `nn sounds, program nn` and, when any zone was not placed, `Pads skipped:nn (note)`.
- **[static]** Assignment loop `620E`-`6284`: zone *i* → pad slot *i*; note = `pad_note_effective(i)`; skipped (and counted in `cs:651C`) if the note is outside 23h-62h or already used in this run (64-bit bitmap at `cs:6528`); otherwise entry byte 0 = Sound number, and with a mute group entry byte 6 = 1 and the slot's group set by `207C`.

### Making the Sounds (`1AED`)

- **[static]** Checks before allocating: zones active (`cs:15B0`), 1-64 zones (`cs:15B3`), the selected zone in range, and the Edit Sound page still showing the zone source unchanged (number `cs:15CE`, name `cs:15B5`, stereo flag and length); else result `FEFEh` (`Sounds not made`). Each zone must end after it starts (`FEFFh`), be at least `558h` frames long (`FEFDh`, `Zone too short`) and lie inside the source. Then `sound_free_records` ≥ zones (else `FFFDh`, `Not enough sound records`) and `sound_free_words` ≥ the total length, doubled for stereo (else `FFFEh`, `Not enough sound memory`).
- **[static]** Per zone: name it, `sound_allocate`, copy settings from the source, set length and end, copy the wave data (twice for stereo), store the new Sound number at `cs:26DC[n]`.
- **[static]** If an allocation fails part-way, the Sounds already made are freed in reverse order with `sound_free(n, 0, 1)` (`1DD9`-`1E05`): no orphan Sounds are left.
- **[static]** Names: on this path the base name from the Names field (`cs:15B5`) plus the zone number; if `sound_find` finds that name, or the number is marked in the bitmap `cs:6576`, 100 is added and it tries again (up to 65,000). A new Sound never takes an existing Sound's name. The Edit Sound `CHOP ZONE` path names Sounds `ZONE001`-`ZONE999` instead (`1E7C`).

### Mute groups and how they are saved

- **[static]** Table at `7E00:23A2`: 24 programs × `21h` bytes. Byte 0 = groups on for that program (`206A`); bytes 1-32 = one 4-bit group per **pad slot** (slot `s`: byte `1 + s/2`, low nibble for even `s`). Helpers: `207C` set one slot, `20BA` fill, `20DC` address of a program's entry, `20EA` clear.
- **[static]** Saving: the PGM and APS save routines' final `file_close` calls are replaced by calls to `21F1` / `221B`, which write a 16-byte header and the table data, then close the file (`22E1`). Header for PGM: `MUTEGP35`, `01 01`, header length `0010h`, record length `0021h`, count `0001h`; for APS the type byte is `02` and the count field 0 (the program count comes from the caller).
- **[static]** Loading: `2177` / `21AE` replace the load routines' `file_close`; they read 16 bytes, compare them with the header, and only then read and check (`2353`) the data and copy it into the table (`224A`).
- **[hypothesis]** Stock systems ignore the trailer because they read fixed sizes and close the file. Consistent with the README's claim; not tested here.

### Where the behaviour can be changed

- **[static]** Ten places inside this page and executor carry no relocated word (neither in the MZ table nor in 3K PLUS's own table) and receive no direct branch from outside the code they replace: `5B82`, `5C21`, `5C2A`, `5C33`, `5C69`, `5CED`, `606E`, `60F5`, `61D8`, `620E` (the last replaces the whole loop to `6285`). Their original bytes are pinned. Every reference to the field variable `cs:6519` is at one of them or at `5B88` (reset to 0).
- **[open]** Jump tables were not searched for targets inside these ranges; only direct branches were.

## Evidence

- **Documented:** 3K PLUS 1.0 README.txt.
- **Static:** decoded from `mpc3000-3kplus-1.0-sys` with LLDB's 16-bit x86 decoder, 2026-11-15/16: starting from the `<To program>` string, the program-record call in the cave and the `7E00h` far references from 3.16 code; branch-target scan over every byte position of the resident cave; MZ and 3K PLUS relocation tables decoded and compared. Pins in [../pins/mpc3000-3kplus-1.0-sys.csv](../pins/mpc3000-3kplus-1.0-sys.csv) (finding `mpc3000.3kplus-lazy-chop`).
- **Emulator (CPU only, supporting):** Unicorn 2.1.4, 2026-11-15/16: the original assignment loop `620E` run on 200 synthetic program states behaved as described here. Not MAME.
- Nothing here has been run in MAME or on hardware.

## Open questions

- [Is RAM above the 3K PLUS cave free at run time?](../questions/3kplus-free-ram-at-runtime.md)
- [Program entry fields and record size](../questions/program-entry-fields.md)
