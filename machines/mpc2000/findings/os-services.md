---
id: mpc2000.os-services
title: OS 1.72 services used by added code (software interrupts, screen, voice and editor routines)
machine: mpc2000
area: os
firmware: ["mpc2000-v1.72-sys", "mpc2000-v1.72-exe"]
status: documented
hardware_tested: no
summary: Software interrupts INT 2Ah-6Ch and about 40 far routines in OS 1.72, with their arguments as used by a published mod. Entry points were checked against the bytes; meanings and arguments are from the mod source and untested here.
contributors: ["open-akai-research"]
last_verified: 2026-11-13
sources: ["vubeatz (Dariusz Chynek), mpc2000_2000xl_mod_pack at commit eb8ece6, mods/*.S (PolyForm Noncommercial 1.0.0; facts restated, no code copied)"]
depends_on: ["mpc2000.os-files"]
---

# OS 1.72 services used by added code

What a program loaded alongside OS 1.72 can call, as one mod pack calls
it. Named addresses are in [../symbols/](../symbols/). Disk services are in
[filesystem.md](filesystem.md).

## Claims

- **[static]** Every code address named in this finding is a routine entry or the instruction described in OS 1.72 (method in [os-files.md](os-files.md)). That is all the bytes prove: what each routine does, and its arguments, come from the mod source below.

### Calling conventions

- **[documented]** SYS far routines take word arguments on the stack. Most leave cleanup to the caller (`ADD SP,n`). Exceptions the source names: `edit_signed_byte` (`3B7C:337C`, 11 words, callee pops 22 bytes), `voice_stop` (`3B7C:2810`, callee pops its one word), `editor_commit_value32` (`3B7C:2E62`, `RETF 4`) and `trim_minmax` (`3B7C:827E`, `RETF 14`).
- **[documented]** `draw_resource` (`3000:1E0E`) and `register_events` (`3000:1EDE`) end in RETF but are reached from SYS code as PUSH CS plus a near CALL. Event tables for `register_events` are 5-byte entries: key byte, then far handler.
- **[documented]** Many services take their operands inline after the `INT` instruction and return past them. Do not place code directly after such an `INT` without its operand bytes.

### Software interrupts

| INT | Use (per the mod source) | Class |
|---|---|---|
| `2Ah` | Fatal error with inline message; returns to the main screen, bypassing callers. Vector `0:00A8`, stock handler `0000:0EF7` (EXE) | documented |
| `2Bh` | LCD command interpreter, command bytes inline. `0Eh` x,y,text; `20h` message pop-up; `22h` clear page; `6Ah` six soft-key labels; `68h` one soft-key label; `1Ah` 20-char name from DS:ptr; `60h` clear area; `84h` highlight bar (CH y, CL x, DL w, DH h) | documented |
| `2Ch` | Filesystem services; see [filesystem.md](filesystem.md). Vector `0:00B0`, stock handler `0FE8:06BE` (EXE) | documented |
| `2Dh` | SCSI sector I/O | documented |
| `2Eh` | Draw an ES:BP resource; `22h` draws the system double frame and title | documented |
| `2Fh` | Vector `0:00BC`, handler `0FE8:0490` (EXE); its segment is the EXE's aux segment | documented |
| `35h` | BL=0: direct note dispatch (`3000:1F40`, IRET at `3000:1F6E`) | documented |
| `37h` | Returns the pad bank, AL = 0-3 | documented |
| `42h` | Text-name editor (ES:SI buffer); owns periodic redraws while open | documented |
| `50h` | Reset page handlers before building a page | documented |
| `52h` | Called after a list refresh | documented |
| `5Bh`, `5Dh`-`5Fh`, `64h`-`69h`, `6Ch` | Bind callbacks given as inline offsets in the current CS: MAIN slot, refresh, decrease/increase, F1-F6, four cursor keys | documented |
| `6Bh` | Install six far soft-key callbacks from an inline table | documented |

- **[documented]** Screen resources drawn by `draw_resource` or `INT 2Eh` are byte streams ending in 0: `22h` x,y,w,h,title = window; `1Ah` key(1-6),style,label = soft key; `02h` = select the primary plane; `07h` x,y,text = text.
- **[documented]** The LCD image is three 1920-byte bitplanes (32 bytes per row, 60 rows) at EXE `1F31:DD90`. The mod source composites them by ORing `1F31:E510` and XORing `1F31:EC90` over the first plane; whether the stock display path does the same is not checked.

### Routines

- **[documented]** Screens: `enter_assign` `3000:5478`, `enter_params` `3000:5B40`, `draw_unsigned` `3B7C:01E0` and `draw_signed` `3B7C:0218` (x, y, value dword, digits), value editor `editor_draw` `3B7C:2DF0`, `editor_disable` `3B7C:2DAE`, `text_editor_commit` `3B7C:33BA`.
- **[documented]** Voices and sounds: `note_on` `3000:29F8`, `note_off` `3B7C:1F3C`, `voice_stop` `3B7C:2810` (push voice 0-31), `voice_stop_now` `3B7C:27DE`, `voice_overlap_stop` `3B7C:259A`, `select_program` `3B7C:58A8` (push 0-based index), `audition_stop` `3B7C:62C4`.
- **[documented]** Sample memory: `pool_alloc` `3000:2534` (push length in PCM words as a dword; AX = handle; 130 or more = failure), `pool_release` `3000:25CA`, `pcm_dma_copy` `3B7C:1036` (source dword, destination dword, 0, count), `pcm_zero` `3B7C:11DA` (no error result). The mod copies at most 16 words per call because the panel UART delivers a byte every 320 us and a longer DMA can lose one.
- **[static]** `pool_alloc` begins by adding `0Fh` to the 32-bit length argument, consistent with rounding up to 16 words.
- **[documented]** `div32` `3000:001C`: push divisor dword, then dividend dword; returns DX:AX.
- **[documented]** EXE callbacks: default AFTER-down `0000:09A4`, slider `0000:A82A` (AX = 0-127), empty callback `0000:0EC0`; soft-key far callbacks F1-F6 at `1F31:0D84` (6 x 4 bytes); LOAD page soft keys set at `0000:E1B5`. `0FE8:5A94` sends to external MIDI. `0FE8:5DA6` auditions.
- **[static]** `0000:0EC0` is a single `RET`.

### Hardware facts stated in the source

- **[documented]** The CPU is an NEC V53. Its word DMA needs an even destination address.
- **[documented]** 32 voices. Sample rate 44.1 kHz (the mod converts lengths with 441 per 10 ms).
- **[hypothesis]** The panel is read through a UART at about one byte per 320 us. Stated in a comment; the device and rate are not checked here.

## Evidence

- Documented: every meaning, argument list and convention above comes from comments and call sites in the vubeatz mod source. Its README says the package itself was not assembled, run in an emulator or tested on hardware.
- Static: entry points checked against `mpc2000-v1.72-sys` and `mpc2000-v1.72-exe` as described in [os-files.md](os-files.md), 2026-11-13. The `pool_alloc` rounding and `0000:0EC0` RET are visible in the first instructions (pinned).
- Nothing here has been run on hardware or in an emulator by this project.

## Open questions

- [How OS 1.72 is loaded and where it runs](../questions/os-load-path.md)
