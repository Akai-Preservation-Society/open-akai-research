---
id: mpc2000xl.address-model
title: How addresses work on the MPC2000XL (file, physical, runtime)
machine: mpc2000xl
area: cpu
firmware: ["mpc2000xl-os1.20"]
status: static
hardware_tested: partial
summary: The OS runs from a RAM copy where segment × 16 + offset equals the file offset. This gives the address forms, the boot page-register map, and the run-time remapping of the top half of that copy that every mod must respect.
contributors: ["open-akai-research"]
last_verified: 2026-10-07
sources: ["NEC V53 user's manual (page registers, printed pp.67-71 and 121-123)"]
depends_on: ["mpc2000xl.rom-and-flash"]
---

# How addresses work on the MPC2000XL

The MPC2000XL maps its ROM differently from the MPC3000, even though both
use a V53. Do not carry address arithmetic from one machine to the other.

## The address forms

| Form | Meaning | Example |
|---|---|---|
| File offset | Position in the 512 KiB image (and in `MPC2KXL.BIN`). **The form used by symbols, pins and patches** | `0x30E43` |
| Physical (ROM) | `0x80000` + file offset | `0xB0E43` |
| Runtime `seg:off` | What the OS code uses. For OS code, `seg × 16 + off` = file offset | `267B:A660` = file `0x30E10` |

## Claims

- **[static]** After the boot block's checks pass, it copies file `0x00000-0x77FFF` into RAM at linear address = file offset and starts the OS there. So for OS code and its initialised data, a runtime `seg:off` converts to a file offset by `seg × 16 + off`.
- **[static]** The boot code loads the 64 page registers (I/O `0xFF00-0xFF7E`, one word per 16 KiB page) so that, with extended addressing (XA) on, logical `0x00000-0x7FFFF` maps to itself and logical `0x80000-0xFFFFF` maps to expanded `0x100000-0x17FFFF`, which is CPU DRAM. The flash is therefore not visible to the running OS.
- **[documented]** With XA on, `expanded = ((PGR[(addr >> 14) & 63] & 3FFh) << 14) | (addr & 3FFFh)`. `BRKXA imm8` (`0F E0`) switches XA on and `RETXA imm8` (`0F F0`) switches it off; both jump through interrupt vector `imm8` without pushing a return address.
- **[static]** Global OS data is segment `0FE7` (`DS = ES = SS = 0FE7`, `SP = 0A7C` at the OS's cold entry). Program and application data is segment `582B`.
- **[static]** The OS remaps part of its own image while it runs. `INT E7` (`0000:180B`) clears the flag byte `0FE7:0067` and rewrites PGR15-32 (logical `0x38000-0x7FFFF`); `INT E8` (`0000:1838`) restores those 18 registers from the boot table and sets `0FE7:0067` again. While a remap is open, code and data above logical `0x38000` are not what the image holds.
- **[static]** Consequence: interrupt code must not enter logical `0x38000` or above unless `0FE7:0067` is set. Stock's own timer handler only reaches high code behind that flag. The segments `35B0` and `582B` are not "low" in this sense: `35B0:7CBA` is page 15.
- **[hardware]** A mod hook reached from the timer interrupt that ignored this crashed every time the user ran SAVE → F5 BOOT, which opens such a remap; routing the hook through a check of `0FE7:0067` fixed it.
- **[static]** The page at file `0x74000-0x77FFF` (segment `7400`) is mapped by PGR30 (port `0xFF3A`), normally `001Dh` (identity) and remapped by `INT E7`. Mod code placed there is safe to call only through a gate that first checks the target's own header bytes.
- **[documented]** Do not read a page register while XA is on. NEC's manual forbids it, and what the chip returns is unknown. Check that a page holds what you expect by reading a signature in it instead.
- **[hardware]** File `0x10036-0x104B3` is 1,149 zero bytes in stock, but code placed there worked after a warm return from flashing and then froze, or crashed at `1000:08F5`, after a cold boot. How that page is mapped at cold boot is not known; treat the range as unusable.
- **[hypothesis]** "Runtime address = file offset" holds for every OS page other than the two exceptions above. It has not been proven page by page.

## Evidence

- **Static:** the boot page-register loops at file `0x7C4FA-0x7C512` and the `INT E7`/`INT E8` handlers were decoded from OS 1.20; the `0FE7:0067` rule from every place that reads or writes the flag. The OS reads PGR33 back once during setup (`0x016FC`), which is how the upper half's mapping was confirmed.
- **Hardware:** the PGR5-gap freezes (images v10-v13, July 2026); the SAVE → F5 BOOT crash and its fix (September 2026); many images with code in segment `7400` benched since September 2026.

## Open questions

- [The PGR5 gap at cold boot](../questions/pgr5-gap.md)
- [Clock and timing on real hardware](../questions/tick-and-clock.md)
