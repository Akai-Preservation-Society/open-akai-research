---
id: mpc2000xl.memory-and-io-map
title: MPC2000XL memory map, I/O ports, interrupts and DMA
machine: mpc2000xl
area: memory
firmware: ["mpc2000xl-os1.20"]
status: static
hardware_tested: partial
summary: Where the flash, RAM and every peripheral sit, the interrupt and DMA lines each uses, and how the OS programs them, from the schematics and the OS 1.20 code.
contributors: ["open-akai-research"]
last_verified: 2026-10-07
sources: ["Akai MPC2000XL main-board schematic", "NEC V53 user's manual"]
depends_on: ["mpc2000xl.hardware-overview"]
---

# MPC2000XL memory map, I/O ports, interrupts and DMA

| Table | File |
|---|---|
| Physical memory | [../hardware/memory-map.csv](../hardware/memory-map.csv) |
| I/O ports | [../hardware/io-ports.csv](../hardware/io-ports.csv) |
| Interrupt and DMA lines | [../hardware/interrupts.csv](../hardware/interrupts.csv) |

Read [address-model.md](address-model.md) before turning any memory
address into a segment and offset.

## Claims

- **[static]** The flash occupies physical `0x80000-0xFFFFF`; the reset vector at file offset `0x7FFF0` is fetched from physical `0xFFFF0`. Unlike the MPC3000, the ROM is not mirrored into the lower half of the first megabyte.
- **[static]** The boot code relocates the V53's on-chip units into I/O `0xC0xx`: timers at `0xC010-0xC016`, interrupt controller at `0xC020`/`0xC022`, DMA unit at `0xC030-0xC03F` (µPD71071 mode).
- **[static]** The OS programs the interrupt controller at file `0x0063D`: edge-triggered, vectors `20h-27h`, self end-of-interrupt (no EOI command is ever needed), initial mask `06h` (inputs 1 and 2 masked).
- **[static]** Interrupt inputs: 0 SMPTE option, 3 disk (floppy or IDE), 4 receive (panel link and both MIDI inputs share it), 5 the system tick from timer 1, 6 MIDI OUT B transmit, 7 MIDI OUT A transmit.
- **[static]** DMA channels: 0 SCSI, 1 floppy or IDE, 2 sample input, 3 L6028 transfers. The DMA mask register is `0xC03F`.
- **[static]** The display is two controllers at I/O `0x60`/`0x62` and `0x100`/`0x102` (bit 7 of status = busy), with the contrast latch at `0x120`. Earlier community notes that called these ports a MIDI controller were wrong.
- **[static]** MIDI is at `0x180-0x186` (SIO1) and `0x1A0-0x1A6` (SIO2). SCSI is at even ports `0x0000-0x001E`.
- **[hardware]** The LED latches answer at `0x140-0x15F` and `0x160-0x17F` exactly as the schematic's decoder predicts ([panel-protocol.md](panel-protocol.md)).
- **[static]** Optional devices the OS drives when fitted: an IDE/ATAPI port at `0x1E0-0x1EE` (ZIP 250 or CompactFlash), an ICS2008 SMPTE chip at `0x1C0-0x1C6`, and an effects board through `0xA0`/`0xA2`.
- **[hypothesis]** The `0xA0`/`0xA2` interface is the EB16 effects board: the OS only writes it and never checks that it is present.
- **[open]** What else the board decodes in `0xC000-0xC03F` beyond the relocated V53 units and the panel receive ports `0xC000`/`0xC002`.

## Evidence

- **Static:** port uses found by scanning OS 1.20 for `IN`/`OUT` instructions with constant ports and reading each site, cross-checked against the schematic's chip selects and the NEC manual's register definitions (2026-07 to 2026-10). The interrupt-controller initialisation bytes are pinned in [../pins/mpc2000xl-os1.20.csv](../pins/mpc2000xl-os1.20.csv).
- **Hardware:** LED latch addresses, 2026-10-07 (see the panel finding).

## Open questions

- [The L6028 sample engine](../questions/sample-engine.md)
- [Clock and timing on real hardware](../questions/tick-and-clock.md)
