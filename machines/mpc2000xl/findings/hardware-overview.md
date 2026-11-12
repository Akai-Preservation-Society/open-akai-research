---
id: mpc2000xl.hardware-overview
title: MPC2000XL hardware overview
machine: mpc2000xl
area: hardware
firmware: ["hardware"]
status: documented
hardware_tested: partial
summary: The chips on the MPC2000XL main and operation boards and what each one does, from the schematics, the user manual and board photographs.
contributors: ["open-akai-research"]
last_verified: 2026-10-07
sources: ["Akai MPC2000XL main-board schematic (MAIN 1-3 and OPERATION sheets)", "Akai MPC2000XL analog-board schematic", "Akai MPC2000XL user manual", "NEC V53 user's manual"]
---

# MPC2000XL hardware overview

Start here to learn what the machine is made of. Ports and addresses are in
[memory-and-io-map.md](memory-and-io-map.md) and in [../hardware/](../hardware/).

## Claims

- **[documented]** Main CPU: NEC µPD70236, annotated `V53A` on the schematic. An 8086-compatible core with on-chip DMA, timer and interrupt units and 64 page registers. The external crystal (X10) is marked 32 MHz.
- **[hypothesis]** The core runs at 16 MHz (half the crystal), as on the MPC3000. The fitted chip's suffix and the internal clock have not been confirmed.
- **[documented]** OS storage: IC20, a 512 KiB 27C040-footprint part. Jumper JP20 selects flash (1-2) or EPROM (2-3). As shipped it is flash and the OS is updated from disk inside the unit.
- **[documented]** CPU work RAM is DRAM (IC70/IC71 or the alternative IC70A/IC71A) behind an XC9572 CPLD (IC40, "CPURAM64").
- **[documented]** Sample memory is separate DRAM on the L6028 DSP's own bus (2 MB standard, 32 MB maximum on two SIMMs), not in the CPU's address space.
- **[documented]** Audio: Akai L6028 DSP (IC200), AK5340 stereo ADC (IC420), PCM69AP stereo DAC (IC720), 11.2896 MHz audio clock. An optional effects board connects at J330.
- **[documented]** Front panel: a separate NEC µPD78C10 microcontroller (IC250 on the OPERATION sheet) with its own 32 KiB EPROM (IC270) scans the pads, keys, DATA wheel and NOTE VARIATION slider, and reports to the main CPU over a serial link.
- **[documented]** Keys are a matrix (K0-K15) through 74HC259, 74HC138 and 74HC573 parts, scanned by the panel MCU.
- **[documented]** The 13 panel LEDs are not driven by the panel MCU but by the main CPU, through two 74HC259 latches (IC220, IC520 on the OPERATION sheet).
- **[documented]** MIDI: Fujitsu MB89371A dual serial controller (IC100). SCSI: Fujitsu MB89352A (IC80), 8 MHz. Floppy: NEC µPD72068 (IC50), 8 MHz. Display: a 248 × 60 graphic LCD module on two controllers.
- **[documented]** No battery-backed RAM, NVRAM or real-time clock appears on any schematic sheet.
- **[documented]** Designators repeat between sheets: on the main board IC250 is a DRAM and IC220 a CPLD; on the OPERATION sheet IC250 is the panel MCU and IC220 an LED latch.
- **[hardware]** One photographed main board carries a Hyundai GM71C18163CT6 DRAM at MAIN IC250, board code 4014A501A, with both SIMM sockets populated.
- **[open]** The CPLD equations (IC40 and the wave-RAM CPLD), and so the exact address decode, are not known.

## Evidence

- Part numbers and nets from the MPC2000XL main-board and analog-board schematics (the freely circulated PDFs), cross-checked against firmware accesses where a device has registers. The LED latch wiring was confirmed on hardware; see [panel-protocol.md](panel-protocol.md).
- The DRAM marking from photographs of one detached board; those photos do not establish its RAM capacity or revision.

## Open questions

- [The L6028 sample engine](../questions/sample-engine.md)
- [Clock and timing on real hardware](../questions/tick-and-clock.md)
