---
id: mpc3000.memory-and-io-map
title: MPC3000 memory map, I/O ports, interrupts and DMA
machine: mpc3000
area: memory
firmware: ["hardware"]
status: documented
hardware_tested: no
summary: Where ROM, RAM, NVRAM and every peripheral sit, and which interrupt and DMA line each device uses, as modelled by the MAME driver.
contributors: ["open-akai-research"]
last_verified: 2026-09-21
sources: ["MAME src/mame/akai/mpc3000.cpp by R. Belmont", "NEC 16-bit V-Series Microprocessor Data Book (1991)"]
depends_on: ["mpc3000.hardware-overview"]
---

# MPC3000 memory map, I/O ports, interrupts and DMA

The tables are kept as CSV so tools and agents can read them:

| Table | File |
|---|---|
| 24-bit physical memory | [../hardware/memory-map.csv](../hardware/memory-map.csv) |
| I/O ports | [../hardware/io-ports.csv](../hardware/io-ports.csv) |
| Interrupt and DMA lines | [../hardware/interrupts.csv](../hardware/interrupts.csv) |

Memory addresses here are 24-bit physical addresses. Code does not use
them directly: read [address-model.md](address-model.md) before turning
any of them into a segment and offset.

## Claims

- **[documented]** Physical memory: OS ROM at `0x000000-0x07FFFF` (mirrored at `0x080000-0x0FFFFF`), work RAM at `0x300000-0x3FFFFF`, NVRAM window at `0x500000-0x500FFF`.
- **[documented]** I/O is 16-bit, and most devices answer only on the low byte of each word, so their registers sit at even port numbers.
- **[documented]** Interrupts: IRQ0-2 are the CPU's own timer outputs; IRQ3 is the floppy and SCSI controllers ORed together; IRQ4 is any MIDI transmitter ready; IRQ5 is UART receivers 1-3; IRQ6 is SMPTE sync in; IRQ7 is UART receiver 4.
- **[documented]** UART wiring: receiver 1 is MIDI IN 1, receiver 2 is MIDI IN 2, receivers 3 and 4 are both tied to the panel microcontroller's transmit line; transmitters 1-4 are MIDI OUT 1-4.
- **[documented]** DMA: channel 0 SCSI, channel 1 floppy, channel 3 the sample DSP.
- **[hypothesis]** DMA channel 2 goes to IC31. The MAME author guesses a direct audio stream.
- **[static]** The firmware agrees with this map where it has been read: the boot code maps work RAM frames from `0x300000`, the LCD character path writes ports `0x00E2` then `0x00E0`, and page 61 is pointed at `0x500000`. See [address-model.md](address-model.md) and [bios-services.md](bios-services.md).
- **[open]** Nothing here has been measured on a board. A schematic or a PAL readout could correct it.

## Evidence

- MAME `mpc3000.cpp`: the program map, the I/O map, the machine configuration (interrupt and DMA callbacks) and the header comment. Port ranges in the CSV are copied from the I/O map.
- The agreement between the firmware and the map is from static analysis of the `mpc3000-vailixi-3.50` image, described in the findings linked above.

## Open questions

- [PAL address decode](../questions/pal-address-decode.md)
- [Ports C010h and C011h](../questions/icu-ports-c010-c011.md)
- [What is on DMA channel 2](../questions/dma2-ic31.md)
- [NVRAM layout](../questions/nvram-layout.md)
