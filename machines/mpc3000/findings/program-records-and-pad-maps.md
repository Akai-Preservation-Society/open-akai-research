---
id: mpc3000.program-records-and-pad-maps
title: Program records, per-note entries and pad-to-note maps in OS 3.16 (and 3K PLUS)
machine: mpc3000
area: os
firmware: ["mpc3000-3kplus-1.0-sys", "mpc3000-v3.16-sys"]
status: static
hardware_tested: no
summary: A program record holds 64 per-note entries (notes 35-98, 18h bytes each; first byte = Sound number, FFh = none) at +3Eh and its own 64-byte pad-to-note map at +73Eh. DS:8063 selects that map (PROGRAM) or the global one at DS:8064 (MASTER).
contributors: ["open-akai-research"]
last_verified: 2026-11-16
depends_on: ["mpc3000.os316-structure", "mpc3000.3kplus-structure"]
---

# Program records, per-note entries and pad-to-note maps

What a program stores per pad and per note, and how a pad is turned into a note.
Needed for anything that assigns Sounds to pads.

The code described here is OS 3.16's. It was decoded in the 3K PLUS 1.0 file, where
it is unchanged except that 3K PLUS hooks the start of `program_init` (see
[3kplus-structure.md](3kplus-structure.md)). Addresses are relative `seg:off` of OS
3.16; file offsets are the same in `mpc3000-v3.16-sys` wherever the pins for this
finding match that file. They are pinned here for `mpc3000-3kplus-1.0-sys` only,
because no copy of the 3.16 file was at hand: check with `oar.py pin` on yours before
relying on them for 3.16.

## Claims

### Where programs live

- **[static]** `program_record(n)` (`302F:0029`, file `0x37D19`) reads a header at relative segment `485F`: word `+0` = record size, word `+2` = program count. It returns the far pointer `485F:(4 + n × size)`, or 0 when `n` ≥ the count.
- **[static]** Both header words are 0 in the file: they are set at run time. A program number 0-23 can therefore have no record.
- **[hypothesis]** The record size is `77Eh`. Reasons: the last field the initialiser writes is `+73Eh`..`+77Dh`, and 24 records of `77Eh` plus the 4-byte header end just below the Sound segment `539Dh`. Confirm by reading `485F:0000` in an emulator.
- **[static]** `program_select(n)` (`19F9:1BF3`) sets `DS:E2E6`/`E2E8` to the record pointer and `DS:E2FB` to `n`, then updates display and mixer state. It is not a pure read.

### Record layout (as `program_init` writes it)

- **[static]** `program_init(n)` (`207C:02D3`, body from `02D9`): name at `+00` (11 bytes from `DS:698F`, then the program number formatted by `2CEC:0009`); defaults at `+11`-`+1A`, `+1C`, `+1F` and a word table from `+22`; **64 per-note entries at `+3Eh`**, each initialised by `207C:01DF`; 64 four-byte entries at `+63Eh` (initialised by `207C:025A`); **a 64-byte pad-to-note map at `+73Eh`** copied from `DS:8064`.
- **[static]** Per-note entry (`18h` = 24 bytes), as `207C:01DF` initialises it: **byte 0 = Sound number, `FFh` = no Sound**; bytes 1-17h get fixed defaults (byte 6 = 0).
- **[static]** The entries are indexed by **note − 35** (`23h`), for notes 35-98. Code that assigns a Sound to a pad computes `record + 3Eh + (note − 23h) × 18h`.
- **[hypothesis]** 3K PLUS's `<To program>` sets entry byte 6 to 1 when it gives the pad a mute group; byte 6 may be a voice or mute mode. Not traced.
- **[open]** Meaning of entry bytes 1-17h and of the record fields at `+11`-`+3Dh` and `+63Eh`.

### Pads to notes

- **[static]** `DS:8063` is the **Mode** field of the *Assign Pads to Note Numbers* page (registered at file `0x1D870`-`0x1D89B`, image `15E70h`, through `field_add_choice`; choices from the far-pointer list at `DS:4B22`: index 0 `PROGRAM`, 1 `MASTER`). Its only direct write sets it to 0 (PROGRAM) at start-up (file `0x0C4BF`).
- **[static]** `pad_note_effective(slot)` (`301D:000A`): slot ≥ 40h → 23h; MASTER → `DS:8064[slot]` (the global map, `pad_notes`); PROGRAM → `[DS:E2E6] + 73Eh + slot` (the current program's own map).
- **[static]** `pad_note_set(slot, note)` (`301D:0070`) clamps the note to **`22h`-`62h`** and writes it to the global or the current program's map by the same rule. A pad can therefore hold note 34 (`22h`), which has no per-note entry: such a pad can never play a Sound.
- **[static]** `pad_first_for_note(note)` (`301D:003B`) returns the first slot whose effective note equals `note`, or −1 (also for notes below 23h). 3K PLUS has its own faster copy at `7E00:2BD2` with the same `DS:8063` rule.
- **[static]** A pad slot is `bank × 16 + pad − 1` (bank A = 0). 3K PLUS prints a slot `n` as letter `(n >> 4) + 'A'` and number `(n & 0Fh) + 1` (`7E00:6070`-`608C`).
- **[static]** Consequences for code that assigns Sounds: several pads can share one note (and then one Sound and one set of entry settings); a pad on note 34 cannot be assigned; and a pad is "occupied" when its note's entry byte 0 is not `FFh`, a test that must read the map of the *destination* program (PROGRAM mode) or the global map (MASTER mode).

## Evidence

- **Static:** decoded from `mpc3000-3kplus-1.0-sys` with LLDB's 16-bit x86 decoder, 2026-11-15/16, following callers from `program_record` and from 3K PLUS's `<To program>` code. Choice strings and the page title read from DGROUP initialised data. Pins in [../pins/mpc3000-3kplus-1.0-sys.csv](../pins/mpc3000-3kplus-1.0-sys.csv) (finding `mpc3000.program-records-and-pad-maps`).
- **Emulator (supporting, CPU only):** in Unicorn 2.1.4 the real `program_record`, `pad_note_effective`-equivalent paths and 3K PLUS's assignment loop were run on synthetic program tables built to this layout (record size set to `77Eh` by the harness); results matched the layout described here. This does not test the record size, which the harness chose.
- Nothing here has been run in MAME or on hardware.

## Open questions

- [Program entry fields and record size](../questions/program-entry-fields.md)
