---
id: mpc2000xl.abi-and-hooks
title: Calling conventions, OS services and hook patterns proven on hardware
machine: mpc2000xl
area: os
firmware: ["mpc2000xl-os1.20"]
status: hardware
hardware_tested: partial
summary: How OS 1.20 code calls and is called, the inline-operand software interrupts, the interrupt controller and tick rules that keep a mod from freezing the machine, and five ways of hooking the OS that have run on hardware.
contributors: ["open-akai-research"]
last_verified: 2026-10-07
sources: ["NEC V53 user's manual (interrupt controller, timer unit)", "Akai MPC2000XL main-board schematic"]
depends_on: ["mpc2000xl.address-model", "mpc2000xl.memory-and-io-map"]
---

# Calling conventions, OS services and hook patterns proven on hardware

## Claims

### Calling convention

- **[static]** OS routines are far calls with arguments pushed right to left; a far callee finds its first argument at `[BP+6]`. Far pointers are pushed segment first, then offset. The **caller** removes the arguments with `ADD SP,n` after the return.
- **[hardware]** A mod that forgot `ADD SP,n` after a far call froze the machine.
- **[static]** Callees preserve `BP`, `SS`, `DS` and `SP`. `PUSH CS` followed by a near `CALL` gives a `RETF` routine a far frame.
- **[static]** Mod code called from application context should save the caller's `DS`, load `582B` (or `0FE7` for global OS data) and restore `DS` before `RETF`.
- **[open]** Stack headroom in each context. Keep mod stack use small.

### Inline-operand software interrupts

- **[static]** `INT 8Fh`, `96h`, `97h` and `9Ch` read operand bytes that follow the `INT` instruction and return past them. Never place ordinary code straight after one; the following bytes are data, and a linear disassembly of such code is wrong.

  | Service | Bytes | Use |
  |---|---|---|
  | `INT 8Fh` function `05h` | `CD 8F 05 col row "text" 00` | Print an inline string |
  | `INT 8Fh` function `1Ch` | `CD 8F 1C "title" 00` | Window title |
  | `INT 8Fh` function `19h` | `CD 8F 19 key style "label" 00` | Soft-key label, key 2-6 = F2-F6 |
  | `INT 96h` | `CD 96 dw event, off, seg` | Register a soft-key callback |
  | `INT 90h` function 6 | string at `ES:SI` | Print a string |

- **[hardware]** A pop-up window drawn and keyed entirely with these services worked on hardware.
- **[static]** The `INT 8Fh` handler entry is file `0x1A9B0`. A read-only breakpoint there logs every text record the OS draws, which is a cheap way to test screens in an emulator.

### The tick, and how not to freeze the machine

- **[static]** Timer 1 (`TOUT1`, interrupt input 5, vector `25h`) is the system tick. It runs one-shot: the handler parks it at `FFFFh` on entry and re-arms `03E8h` (1,000 counts) on exit, so the real period is 1 ms plus the handler's own run time.
- **[static]** Foreground delays wait on the tick: `0000:168D` waits until the millisecond counter `0FE7:0B8A` has advanced by `CX`, with no timeout. A lost tick therefore freezes the machine at the next delay (during boot, a load or a pop-up), even with nothing playing.
- **[static]** The interrupt controller's mask register is `0xC022`. A request raised while its input is masked stays pending and is taken when the mask is cleared.
- **[documented]** Set a mask bit only with interrupts disabled. If a request is withdrawn while the CPU can acknowledge it, the controller answers with vector `27h` without marking it in service; here vector `27h` is the MIDI OUT A transmit handler, which then sends a byte unconditionally. Clearing a mask bit needs no such care.
- **[static]** Outside the boot block, only three places in OS 1.20 write `0xC022`: initialisation, the tick handler (it masks its own input on entry and unmasks it before returning) and a register-dump monitor.
- **[open]** The tick period on real hardware has not been measured.

### Remapping rules

- **[static]** Do not call `INT E8h` to repair the page mapping from mod code: the OS pairs its own `INT E7h`/`INT E8h` calls, and an extra `INT E8h` while a remap is open makes later OS I/O use the wrong map.
- **[static]** Interrupt-reachable mod code must not enter logical `0x38000` or above while `0FE7:0067` is clear ([address-model.md](address-model.md)).

### Hook patterns that have run on hardware

- **[hardware]** These patterns have each run on real units in released or benched images:

  | Pattern | What changes | Notes |
  |---|---|---|
  | Swap an event-table callback | 4 bytes: an event record's `seg:off` | Easiest to undo. Event records are an event byte followed by a far pointer |
  | Near call → far call | `E8 rel16` plus following bytes become `9A off seg` | The far target ends with `RETF` and must replay what the replaced bytes did |
  | Inline far-call rewrite | An instruction pair becomes `9A off seg`, plus a `JC` to the stock exit | Keeps the stock path as fallback when the hook declines |
  | Far call into a gate | A short call into a low-memory gate that checks the target module's header and falls back to stock if it is missing | Required for code at segment `7400` |
  | Same-length string patch | Text bytes only | e.g. the VER field at file `0x30E43` |

- **[static]** Prefer keeping the stock path as the fallback whenever mod code cannot run.

## Evidence

- **Static:** OS 1.20 code; the interrupt-controller facts from the NEC V53 user's manual (printed pp.147-164 and 236) combined with the OS's own initialisation (`0x0063D-0x0065A`) and tick handler (`0x0084D-0x008B8`), both pinned.
- **Hardware:** the patterns are those of the 2KXL PLUS images (v1.1 to v1.3.2, released September-October 2026) and earlier bench images; the `ADD SP` freeze and the version-string patch from July 2026 benches.

## Open questions

- [Clock and timing on real hardware](../questions/tick-and-clock.md)
- [A map of the OS 1.20 code](../questions/os120-code-map.md)
