---
id: mpc3000.interrupt-vectors
title: Interrupt vector table after boot
machine: mpc3000
area: os
firmware: ["mpc3000-vailixi-3.50"]
status: static
hardware_tested: no
summary: Which code owns each interrupt vector once the OS has started, who installs it, and how to install a handler the way the OS does.
contributors: ["open-akai-research"]
last_verified: 2026-09-21
depends_on: ["mpc3000.address-model", "mpc3000.calling-conventions"]
---

# Interrupt vector table after boot

Established on the Vailixi 3.50 reference image, by following the reset
path until the OS has installed its handlers.

## Claims

- **[static]** The live vector table is in RAM at `0000:0000` (24-bit `0x300000`). The vectors at the start of the EPROM (linear `0x00000-0x00053`) are used only for the first mode switches: slot `11h` → `FAC0:001F`, slot `12h` → `FAC0:024F`, slot `14h` → `FAC0:0134`.
- **[static]** The BIOS fills all 256 vectors. Slots `20h-FFh` get `F800:1952`, a single `IRET`. Slots `00h-1Fh` get a ladder of 3-byte stubs starting at `F800:1953` that all call one routine, which prints `System Error ... software bug of type NNh` with the vector number. So an unexpected interrupt below `20h` halts on an error screen and one above is ignored.
- **[static]** Vectors that differ from those defaults once the OS is up:

  | Vector | Handler | Installed by | Purpose |
  |---|---|---|---|
  | `00h` | `FB00:02F8` | AMX kernel | kernel-managed |
  | `04h` | `FB00:02EF` | AMX kernel | kernel-managed |
  | `08h` | `D52A:0008` | OS, through the kernel | OS interrupt handler |
  | `0Bh` | `F800:2047` | BIOS | BIOS handler |
  | `0Ch` | `D5DD:000C` | OS, through the kernel | OS interrupt handler |
  | `0Dh` | `D547:0067` | OS, through the kernel | OS interrupt handler |
  | `0Eh` | `D5F3:000E` | OS, through the kernel | OS interrupt handler |
  | `0Fh` | `F800:1952` | BIOS | ignored (`IRET`) |
  | `10h` | `FAC0:01A4` | boot code | load third page table |
  | `40h` | `F800:1B36` | BIOS | BIOS service |
  | `41h` | `F800:0364` | BIOS | file services |
  | `42h` | `F800:205E` | BIOS | BIOS service |
  | `43h` | `F800:16AA` | BIOS | LCD services |
  | `45h` | `F800:0143` | BIOS | MZ loader |
  | `46h` | `F800:18D6` | BIOS | BIOS service |

- **[static]** The OS installs a handler by far-calling the kernel routine at `FB00:0347` with the vector number in `DL` and the handler address in `ES:BX`. The kernel refuses vectors 0 and 4, which it keeps for itself, and a null address installs an `IRET`.
- **[static]** Each OS interrupt handler begins with a far call to the kernel's interrupt wrapper at `FB00:0157`. A handler added to the OS should do the same so the kernel can switch tasks on the way out.
- **[static]** A later code path installs vector `09h` → `D61A:000A`, and the hand-off to a floppy program re-points vector `08h` at a small BIOS-range stub.
- **[hypothesis]** Vectors `08h-0Fh` are the eight hardware interrupt lines IRQ0-IRQ7 in [../hardware/interrupts.csv](../hardware/interrupts.csv), in that order, which would make `0Ch`/`0Dh` the MIDI transmit and receive handlers. The base vector programmed into the on-chip interrupt controller has not been read, so this is not established.
- **[open]** What each OS handler does, and what vectors `40h`, `42h` and `46h` offer.

## Evidence

- Static decoding of `mpc3000-vailixi-3.50` along the reset path (2026-09-21): every store into the vector table was located, and the resting table was reconstructed from them. This is one path through the code, not a proof that no other code writes the table later.
- The BIOS fill routine, the default `IRET` and the EPROM vector template are pinned in [../pins/mpc3000-vailixi-3.50.csv](../pins/mpc3000-vailixi-3.50.csv).

## Open questions

- [Ports C010h and C011h](../questions/icu-ports-c010-c011.md)
- [A code map for the stock OS images](../questions/stock-os-code-map.md)
- [MIDI handling](../questions/midi-handling.md)
