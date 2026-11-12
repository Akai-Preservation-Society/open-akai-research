---
id: mpc2000xl.boot-and-panel-handshake
title: Boot path and the panel ID handshake
machine: mpc2000xl
area: boot
firmware: ["mpc2000xl-os1.20", "mpc2000xl-panel-v1.00"]
status: static
hardware_tested: partial
summary: From the reset vector to the OS. The boot block sets up the V53, waits for the panel MCU to send the ID bytes E0 11, checks the OS image and copies it to RAM. An emulator must answer the ID wait to boot.
contributors: ["open-akai-research"]
last_verified: 2026-09-21
depends_on: ["mpc2000xl.rom-and-flash", "mpc2000xl.address-model"]
---

# Boot path and the panel ID handshake

## Claims

- **[static]** Reset: far jump from file `0x7FFF0` to `FC00:0400` (file `0x7C400`). The boot code writes the V53 system registers (`0xFFE0-0xFFFE`: wait states, refresh, relocation of the on-chip units to `0xC0xx`), the timers, the interrupt controller and the DMA unit, then loads the page registers and switches extended addressing on.
- **[static]** The boot block waits for the panel. A receive handler installed for `INT 24h` (code at file `0x7CBF0`) polls `0xC002` bit 1, reads a byte from `0xC000`, stores bytes with bit 7 set at `[0070h]` and bytes with bit 7 clear at `[006Fh]`. The boot loop at file `0x7C557` then compares the word at `[006Fh]` with `E011h`, or `E022h`, retrying up to 1,000 times.
- **[static]** The panel program sends exactly that: its reset code transmits `E0h` then `11h` over its serial output (panel EPROM `0x011B-0x0279`). It is the only comparison with `E011h` in the OS image.
- **[hypothesis]** `E022h` identifies a different panel program revision. It selects a second initialisation path in the boot block.
- **[static]** After the handshake the boot block checks the OS magic and checksum ([rom-and-flash.md](rom-and-flash.md)), copies file `0x00000-0x77FFF` to RAM, and enters the OS with `DS = ES = SS = 0FE7`, `SP = 0A7C`.
- **[static]** The boot block also contains the disk recovery loader and the flash-programming code, and it identifies the flash chip with a read-ID probe before programming.
- **[hardware]** The unit boots normally with every modified OS image that kept the boot block unchanged; boot behaviour is therefore not affected by changes to file `0x00000-0x77FFF` beyond the checks above.
- **[open]** Which board logic decodes `0xC000`/`0xC002`, and the electrical path between the two processors.

## Evidence

- **Static:** decoded from the OS 1.20 boot block and the panel EPROM (µPD7810 instruction set, MAME's tables). The comparison at `0x7C557` and the receive handler are pinned.
- **Emulator:** an emulator that presents `E0`, `11` through ports `0xC002`/`0xC000` passes the wait and boots OS 1.20 to the main screen.
- **Hardware:** every flash-and-boot of a modified image (July to October 2026) exercised this path unchanged.

## Open questions

- [Commands from the main CPU to the panel](../questions/panel-commands.md)
