---
id: s3200.code-structure
title: Segments, code extents and indirect calls in OS 2.00
machine: s3200
area: os
firmware: ["s3200-v2.00"]
status: static
hardware_tested: no
summary: OS 2.00 has two code segments, 0FE9 (0xFE90-0x1FE7F) and 2033 (0x20330-0x2DF2F), around data segments 0000, 1FFE and 2DF3. A recursive disassembly with resolved indirect targets reaches every instruction seen executing in emulator runs. Eleven indirect sites stay unresolved.
contributors: ["open-akai-research"]
last_verified: 2026-11-02
depends_on: ["s3200.address-model"]
---

# Segments, code extents and indirect calls in OS 2.00

Where code is, where data is, and how much of the code a static pass
can reach. Read [address-model.md](address-model.md) first.

## Claims

- **[static]** Layout (file offsets):

  | Range | Segment | Contents |
  |---|---|---|
  | `0x00000-0x003FF` | `0000` | IVT, RAM entry code, initial stack |
  | `0x00400-0x0805F` | `0000` (DGROUP) | Initialised strings and tables; variables from about `0x6AE0` |
  | `0x08060-0x0FE8F` | `0000` | Zero in the image; run-time buffers (BSS) |
  | `0x0FE90-0x1FE7F` | `0FE9` | Code. `0FE9:0000` is `EB FE`; entry `0FE9:0002`; last instruction is the `RET` at `0x1FE7F` |
  | `0x1FE80-0x1FFD5` | `DFE8` (ROM) | Boot block, run from ROM only |
  | `0x1FFE0-0x20322` | `1FFE` | Help text, read as DS/ES=1FFE |
  | `0x20330-0x2DF2F` | `2033` | Code. Last instruction is the `RET` at `0x2DF2E`, then one pad byte |
  | `0x2DF30-0x352DA` | `2DF3` | Initialised data (strings from `2DF3:0000`) |
  | `0x352DB-0x3FFEF` | `2DF3` | Zero in the image; `2DF3` BSS ([memory-use.md](memory-use.md)) |
  | `0x3FFF0-0x3FFFF` | `FFFF` (ROM) | Reset and loader far jumps |

- **[static]** Far calls in the image target `2033` 914 times and `0FE9` 178 times. No reachable far call targets another segment inside the image. Other segment values the code loads (`4700`, `5000-9000`, `A000-E000`, `BFE8`) are RAM outside the image.
- **[static]** A recursive descent from `0FE9:0002`, following direct flow only, decodes 24,237 instructions with no decode conflicts and no invalid opcodes. It reaches `0xFE92-0x1FE57` in `0FE9` and `0x20330-0x2DE91` in `2033`.
- **[static]** Of 23 indirect call/jump sites, these have targets found in the bytes: `0x105AB` (CS table `0FE9:071E`), `0x11139`/`0x11142` (the 13-entry key/handler table at `DS:04EB` and its default), `0x13C78` (records at `DS:149E`, `14AC`, `14BA`, `14C8`, passed to the copier at `0FE9:3DD2`, which ends in `CALL [BX+0C]`), `0x19E91`, `0x1D3F6` and `0x270E8` (immediate before the call), `0x110C7`, `0x154C5`, `0x1FB40`, `0x1FB50`, `0x2A1DC`, `0x170D1` (partly).
- **[emulator]** Four more sites were resolved only by observing them in emulator runs: `0x1E505` (targets `EAD9`, `EB0F`, `EB3F` via a `2DF3` record word +6), `0x2A0C7`, `0x2A41D`, and the second target `0FE9:7807` of `0x170D1`.
- **[static]** Reseeding the static pass with the found targets and the image's IVT vectors reaches 25,386 instructions and misses 315 of the 7,885 instruction starts executed in the emulator runs. Adding the emulator-only targets reaches 25,895 instructions (67,318 bytes) and misses none. Segment ends do not change.
- **[open]** Seven sites have no known target and never ran: `0x106FA`, `0x110C1`, `0x11100` (UI field records through BX/SI) and `0x27068`, `0x2709A`, `0x270DA`, `0x270DC` (pointer variables `0x7C0F-0x7C2A` with no immediate store found). Code reached only through them is unmapped and may hold more data or variables.
- **[static]** Exceptions inside the code segments are listed in [memory-use.md](memory-use.md): a 7-byte INT 11 handler at `0x7640` inside DGROUP, two sets of variables written through CS inside `2033`, and a data table inside `2033`.

## Evidence

- Static: the contributor's own recursive-descent disassembler (unpublished Python), run 2026-11-02 over the linear image from `0FE9:0002`, plus a far-call histogram (opcode `9A`) and a segment-load census (`MOV DS/ES` with immediates). Anyone can repeat the extents and the end-of-segment `RET`s with `ndisasm -b16` at the offsets pinned: `0xFE90`, `0x1FE5B` (37), `0x2DF20` (24), `0x116D3` (first `DS=2DF3` load), `0x4EB` (58), `0x13C62` (26).
- Emulator: the contributor's own unpublished 8086 emulator in Python, with invented peripheral stubs (no FDC, ICU, serial, timer or LCD model taken from real hardware). Seven runs on 2026-11-02, each one execution, with a pre-registration written before the runs: three boots with port `0x60` = `0xC0`, `0x40` or `0x80` (40,000,000 instructions each), a boot with a blank floppy mounted, a boot with MIDI and SysEx input, a boot that autoloads an OS floppy, and a direct call into SAVE OS. These runs are untested against hardware and cannot yet be repeated by others.

## Open questions

- [Run-time writes and free space, on hardware](../questions/runtime-writes-and-free-space.md)
- [Panel, data wheel and LCD](../questions/panel-and-lcd.md)
