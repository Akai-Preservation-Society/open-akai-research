---
id: s900.hardware-overview
title: S900 hardware from Akai's service manual addendum and owner's manual
machine: s900
area: hardware
firmware: ["hardware"]
status: documented
hardware_tested: no
summary: Akai's S900 CPU-board addendum lists the main chips. They agree with MAME's driver - V30, uPD71071 DMA, uPD71059 ICU, 6850 ACIA, uPD7265 FDC - and add a uPD71051 serial unit, MN41256 DRAM and 16 KiB TMM27128 EPROMs.
contributors: ["open-akai-research"]
last_verified: 2026-11-13
sources: ["Akai S900 Service Manual (Additional), CPU PCB schematic addendum, 'Information of ICs' table, p. 1 (scanned; as hosted on s900fx.com, 2026-11-13)", "Akai S900 Owner's Manual (28 pp., as hosted on s900fx.com), Specifications", "MAME src/mame/akai/s900.cpp at commit c2caa8969adb"]
---

# S900 hardware from Akai's service manual addendum and owner's manual

Chip-level facts for the S900 from Akai's documents.

## Claims

- **[documented]** Specifications: sampling 7.5-40 kHz; sampling time 63.3 s down to 11.75 s; 8 voices; 6-octave range; 750 KB internal memory; built-in 3.5-inch 2DD floppy drive (1 MB unformatted); RS-232C; MIDI IN, OUT and THRU; 8 line outputs, stereo outputs, a mix output and a 13-pin voice output.
- **[documented]** The CPU-board IC table lists: uPD70116C (V30), uPD71011C (clock generator), uPD71051C (serial control unit), uPD71059C (interrupt controller), uPD71071C (DMA controller), uPD7265C (floppy controller), SED9420C (floppy data separator), HD6850P (IC8, ACIA), MN41256A-08 dynamic RAM (IC45-IC72, 28 chips of 256K x 1), TMM27128AD-20 (16 KiB EPROM) and TMM2764D-2 (8 KiB EPROM).
- **[documented]** The uPD71051C is an 8251-compatible serial unit, which fits MAME's "8251 USART for the RS232 port". The RS-232 port runs at a baud rate typed in on MIDI page 05, from 300 to 19,200; the S900 can be controlled from it instead of MIDI.
- **[documented]** The 16 KiB TMM27128 matches the 16 KiB chip files of the known OS sets ([../firmware.toml](../firmware.toml)). What the 8 KiB TMM2764 holds is not stated.
- **[open]** The memory map and I/O decode are drawn on the schematics and the main service manual, which have not been read here.

## Evidence

- Read from scans of Akai's S900 service manual addendum and owner's manual as hosted on s900fx.com, downloaded 2026-11-13. Nothing was checked on a machine.

## Open questions

- [Akai S900: the first things to establish](../questions/first-steps.md)
