---
id: mpc2000xl.panel-protocol
title: Front-panel input reports and the LED latches
machine: mpc2000xl
area: panel
firmware: ["mpc2000xl-os1.20"]
status: hardware
hardware_tested: partial
summary: Every key, pad, wheel and slider event reaches the main CPU as a two-byte report from the panel MCU; this gives each header and its handler. The 13 LEDs are written directly by the main CPU through two latches; each LED's port is confirmed on hardware.
contributors: ["open-akai-research"]
last_verified: 2026-10-07
depends_on: ["mpc2000xl.memory-and-io-map", "mpc2000xl.boot-and-panel-handshake"]
---

# Front-panel input reports and the LED latches

## Claims

### Input reports (panel to main CPU)

- **[static]** The receive routine `0000:0B62` returns at once unless `0xC002` bit 1 is set, then reads one byte from `0xC000`. A byte with bit 7 set is a header, kept at `0FE7:01B8`; a byte with bit 7 clear is the payload and is dispatched on the kept header:

  | Header | Handler | Meaning |
  |---|---|---|
  | `80` | `0000:0BC8` | DATA wheel, counter-clockwise; payload = step count. Accelerates when reports come closer than `28h` ticks |
  | `81` | `0000:0C0A` | DATA wheel, clockwise |
  | `84` | `0000:0C4C` | Key press; payload = key code, translated through the table at `0FE7:0A7E` into the key ring at `0FE7:00B6` |
  | `85` | `0000:0C4C` | Key release (same, with `8000h` set) |
  | `86` | `0000:0C68` | NOTE VARIATION slider, payload = 7-bit position; stored only when it changes (`0FE7:01C8`) |
  | `90`-`9F` | `0000:0C76` | Pad strike on pad slot `n`; payload = peak / 2, `0` = release. Clamped to `76h`, rescaled to 1-127 and stored at `0FE7:04DE + n` |
  | `A0`-`AF` | `0000:0D14` | Pressure on held pad slot `n` |
  | `FF` | `0000:0D28` | Byte stream into a buffer; purpose not identified |

- **[hardware]** DATA wheel direction: `80` is counter-clockwise and `81` clockwise.
- **[static]** Pad slot `n` is the pad within the current bank; the bank is held at `0FE7:04D5` (`0`, `10h`, `20h`, `30h` for A-D).
- **[hypothesis]** `86` is the slider and `A0`-`AF` is pad pressure. The code supports it strongly (the slider value is read exactly where note variation is computed), but no capture of the serial line has confirmed it.
- **[open]** The range of the pressure payload and the slider's travel-to-value curve.

### LEDs (main CPU to latches)

- **[documented]** The 13 LEDs hang off two 74HC259 addressable latches. The data bus is not connected: address bits A1-A3 pick the output and A4 sets its level. Output low lights the LED. So writing any value to port `base + 2 × Q` lights LED `Q`, and to that port `+ 10h` puts it out.
- **[hardware]** The ports, each confirmed by lighting the LEDs one at a time on a real unit:

  | LED | On | Off | | LED | On | Off |
  |---|---|---|---|---|---|---|
  | AFTER | `0x140` | `0x150` | | BANK D | `0x162` | `0x172` |
  | REC | `0x142` | `0x152` | | BANK B | `0x164` | `0x174` |
  | UNDO SEQ | `0x144` | `0x154` | | TRACK MUTE | `0x166` | `0x176` |
  | PLAY | `0x146` | `0x156` | | NEXT SEQ | `0x168` | `0x178` |
  | OVER DUB | `0x148` | `0x158` | | BANK A | `0x16A` | `0x17A` |
  | FULL LEVEL | `0x160` | `0x170` | | BANK C | `0x16C` | `0x17C` |
  | | | | | 16 LEVELS | `0x16E` | `0x17E` |

- **[static]** The OS refreshes all 13 LEDs from flag bytes in segment `0FE7` in one routine (`0000:113B`, with the bank LEDs set by `0000:11F6`), run from the main loop whenever `0FE7:0063` or `0064` is set. A mod's own LED state lasts only until the next refresh, unless the mod suppresses or follows it.
- **[static]** A single `OUT` to an LED port touches no shared state, so it is safe inside an interrupt handler.
- **[hardware]** A lit LED set by a mod stayed lit while the machine was idle, so the OS does not refresh the LEDs on a timer.

## Evidence

- **Static:** OS 1.20 routines `0x00B62-0x00D38` and `0x0113B-0x0121F`; schematic OPERATION sheet (latches) and MAIN 1 (decoder IC73). The receive routine and LED refresh are pinned.
- **Hardware:** 2026-10-07, one unit, a test image that lit each LED in turn as the DATA wheel moved and sent a MIDI message for each step: all 13 LEDs lit in the order of the table, and counter-clockwise turns produced `80` reports. A later image turned every key, pad, wheel and slider report into MIDI in the emulator; its own hardware test has not been run.

## Open questions

- [Commands from the main CPU to the panel](../questions/panel-commands.md)
