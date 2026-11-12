---
id: mpc2000xl.file-formats
title: SND, PGM and ALL file layouts
machine: mpc2000xl
area: file-format
firmware: ["mpc2000xl-os1.20"]
status: hardware
hardware_tested: yes
summary: Byte layouts of the .SND sound file (complete), the .PGM program file (framing and record layout) and the .ALL sequence container (framing), checked against files written by a real MPC2000XL and against the OS's loaders.
contributors: ["open-akai-research"]
last_verified: 2026-07-17
---

# SND, PGM and ALL file layouts

Offsets are within the file. Multi-byte values are little-endian.

## Claims

### `.SND` (one sound)

- **[hardware]** Files written by the machine have a 42-byte (`2Ah`) header followed immediately by signed 16-bit little-endian PCM, interleaved left/right for stereo. PCM size = end frame × channels × 2.

  | Offset | Size | Field | Status |
  |---|---|---|---|
  | `00h` | 2 | Signature `01 04` | hardware |
  | `02h` | 16 | Name, ASCII, space-padded | hardware |
  | `12h` | 1 | Unknown (0 in both samples) | open |
  | `13h` | 1 | Level (100 in both) | hypothesis |
  | `14h` | 1 | Tune, signed (0 in both) | hypothesis |
  | `15h` | 1 | `0` mono, `1` stereo | hardware |
  | `16h` | 4 | Start frame | hardware |
  | `1Ah` | 4 | Loop end (equal to end in both samples) | hypothesis |
  | `1Eh` | 4 | End frame (= frame count) | hardware |
  | `22h` | 4 | Loop length (0 in both) | hypothesis |
  | `26h` | 1 | Loop mode, `0` = off | hardware |
  | `27h` | 1 | Beats (4 in both) | hypothesis |
  | `28h` | 2 | Sample rate, 44100 | hardware |
  | `2Ah` | rest | PCM | hardware |

### `.PGM` (one program)

- **[hardware]** Files written by the machine start `07 04`. The OS reads them through a dispatcher that requires first byte `07h` and branches on the second byte.
- **[static]** Layout (from the loader and serializer, confirmed on an empty program written by the machine):

  | Offset | Size | Field |
  |---|---|---|
  | `00h` | 2 | Signature `07 04` |
  | `02h` | 2 | Number of sample-name rows that follow the metadata (17 bytes each) |
  | `04h` | 2 | Metadata size, `001Eh` |
  | `06h` | 28 | Program metadata, starting with the space-padded program name |
  | `22h` | 2 | Layer count, 64 |
  | `24h` | 2 | Record size, 25 |
  | `26h` | 64 × 25 | Per pad: a signed 1-byte sound reference and the 24-byte layer |
  | `666h` | 652 | Mixer and remaining tables (in an empty program, the note map of 64 bytes, values `23h`-`62h`, sits at `7EAh`) |

- **[static]** In the 24-byte layer, offset `+0` is the play mode and `+5` the voice overlap (`0` poly, `1` mono).
- **[open]** The meaning of most mixer and global-table bytes, and offsets when sample-name rows are present.

### `.APS` and `.ALL`

- **[hardware]** `.APS` (all programs and sounds) files start `0A 05`; the OS reads first-byte-`0Ah` files through a second dispatcher with subtypes 0, 1, 4 and 5. An `.APS` embeds each program with 26-byte records.
- **[static]** The `.ALL` file (all sequences) has a fixed `3846h`-byte prefix with a 99-entry sequence directory, followed by each sequence's image rounded to whole paragraphs; loader at file `0x1DA43`, writer at `0x1F6A9`.
- **[open]** The standalone `.SEQ` format, the event and song layouts inside a sequence, and the `.PAR` file.

## Evidence

- **Hardware:** files written by one MPC2000XL on OS 1.20 (a mono and a stereo sound with known start and length, an empty program, all programs, an empty two-bar sequence), July 2026, with the settings used recorded by the owner. The files themselves are not published here.
- **Static:** loaders and writers in OS 1.20 (`.PGM` dispatcher `0x39342`, `0Ah` dispatcher `0x396E0`, `.ALL` code above).

## Open questions

- [Sequence files and event format](../questions/sequence-format.md)
