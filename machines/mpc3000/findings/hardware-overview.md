---
id: mpc3000.hardware-overview
title: MPC3000 hardware overview
machine: mpc3000
area: hardware
firmware: ["hardware"]
status: documented
hardware_tested: no
summary: The chips on the MPC3000 CPU board and what each one does, taken from the Akai service parts list and the MAME driver.
contributors: ["open-akai-research"]
last_verified: 2026-09-21
sources: ["Akai MPC3000 service manual (parts list)", "MAME src/mame/akai/mpc3000.cpp by R. Belmont", "NEC 16-bit V-Series Microprocessor Data Book (1991)"]
---

# MPC3000 hardware overview

Start here to learn what the machine is made of. Addresses for each
device are in [memory-and-io-map.md](memory-and-io-map.md) and, in
machine-readable form, in [../hardware/](../hardware/).

## Claims

- **[documented]** Main CPU: NEC µPD70236 (V53), marked `µPD70236GD-16`. It is an 8086-compatible core with an 8237-compatible DMA controller, 8254-compatible timers, an 8259-compatible interrupt controller and a serial port on the same chip.
- **[documented]** The crystal is 32.000 MHz and the CPU core runs at half of it, 16 MHz. Emulators that clock the core at 32 MHz run it twice too fast.
- **[documented]** Front panel: a separate NEC µPD78C10AGQ microcontroller at 12 MHz with its own 32 KiB EPROM (AM27C256, IC602). It scans pads, keys and the data wheel and reports to the main CPU over a serial line.
- **[documented]** Sample playback and recording: an L7A1045 L6028 "DSP-A" chip (IC28) clocked at 33.8688 MHz. Sample memory hangs off the DSP's own 16-bit bus with 24 address bits (32 MiB); it is not in the CPU's address space.
- **[documented]** Operating system: two AM27C020 EPROMs (IC13 LS, IC14 MS).
- **[documented]** Work RAM: two HM658512 512K×8 pseudo-static RAMs (IC15, IC16), 1 MiB.
- **[documented]** Settings memory: battery-backed static RAM, listed as an LC3517 (2K×8).
- **[documented]** Floppy: µPD72069 controller. SCSI: Fujitsu MB89352. MIDI: TE7774 quad UART. LCD: LC7981 controller. Sync timers: 8254 (MB89254), separate from the CPU's own timers. Two 8255 (MB89255B) port expanders. Two HC259 latches drive panel LEDs.
- **[documented]** CPU board: L4012A family.
- **[hypothesis]** Address decoding is done by 18CV8 PAL devices (IC25, IC29, IC31). Their equations have not been read; every address in this repository rests on the MAME map and on what the firmware does.
- **[open]** No manufacturer datasheet has been found for the L7A1045 or the TE7774. What is known about them comes from the MAME device models.

## Evidence

- Chip markings: optical character recognition of the Akai MPC3000 service manual parts list (the freely circulated 16-page edition). That edition has parts and disassembly pages; full schematic sheets were not found in it.
- Roles and clocks: MAME `src/mame/akai/mpc3000.cpp` (machine configuration and header comment). MAME marks the driver as not working; its maps and wiring comments are still the best public description. The 33.8688 MHz DSP clock is commented there as verified against a schematic.
- 16 MHz versus 32 MHz: the NEC data book divides the crystal by two for the core; Akai's specifications say "16 MHz V53".

## Open questions

- [PAL address decode](../questions/pal-address-decode.md)
- [Sample engine and DSP registers](../questions/sample-engine-dsp.md)
- [What is on DMA channel 2](../questions/dma2-ic31.md)
- [Front-panel protocol](../questions/panel-protocol.md)
