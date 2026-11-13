---
id: s950.hardware-overview
title: S950 hardware from Akai's service manual and owner's manual
machine: s950
area: hardware
firmware: ["hardware"]
status: documented
hardware_tested: no
summary: The S950 service manual's parts lists name every main chip. They agree with MAME's driver - V30, three uPD71071 DMA, uPD71059 ICU, 6850 MIDI ACIA, uPD72066 FDC, 8254/8253 timers - and add the board, EPROM, DRAM, panel PPI and LCD part numbers.
contributors: ["open-akai-research"]
last_verified: 2026-11-13
sources: ["Akai S950 Service Manual (19 pp., scanned; as hosted on s950fx.com, 2026-11-13): specifications p. 1, parts location pp. 5-6, MIDI implementation chart p. 8, parts lists pp. 9-14", "Akai S950 Operator's Manual (106 pp., as hosted on s950fx.com), Overview and Disk chapters", "MAME src/mame/akai/s900.cpp at commit c2caa8969adb"]
---

# S950 hardware from Akai's service manual and owner's manual

Chip-level facts for the S950 taken from Akai's own documents. They
confirm most of what [../machine.toml](../machine.toml) took from MAME.

## Claims

- **[documented]** Specifications: 12-bit sampling, 7.5-48 kHz; 8 voices; sampling time 63.35 s down to 9.79 s; 750 KB internal memory, expandable with up to two EXM006 boards to 2.25 MB; 3.5-inch floppy for both 2DD and 2HD disks; RS-232C; MIDI IN, OUT and THRU; 8 line outputs, stereo outputs, a mix output and a 13-pin voice output. The owner's manual adds "16-bit processing" and a bandwidth variable up to 19.2 kHz.
- **[documented]** Boards: CPU PCB L6013A5010 (block BA-L6013A040A), voice PCB L6002A5020, panel PCB L6002B504A, power, filter, and several jack boards (MIDI, RS-232C, mic, VR, inverter). The floppy drive block is DFP723D14B. The LCD is DMC40218UE.
- **[documented]** CPU PCB parts list:

  | Ref | Part | Function |
  |---|---|---|
  | IC1 | uPD70116C-8 | V30 CPU |
  | IC2 | uPD71011C | clock generator |
  | IC3-IC5 | uPD71071C x3 | DMA controllers |
  | IC6 | uPD71059C | interrupt controller |
  | IC8 | HD63B50P | 6850-class ACIA (MIDI) |
  | IC9 | uPD72066C | floppy controller |
  | IC10 | SED9420CAC | floppy data separator |
  | IC11, IC12 | MBM27C256-15 x2 | OS EPROMs, 32 KiB each |
  | IC45-IC51 | MB81C4256-10 x7 | 256K x 4 DRAM |
  | X1 | 16.000 MHz | crystal |

- **[documented]** Panel PCB: uPD71055C (8255-class parallel interface) and 28 tact switches. MIDI jack PCB: PC900V opto-isolator and SN74LS05N.
- **[documented]** Voice PCB: MB89254 x3 (IC19-IC21) and uPD8253C-2 x3 (IC22-IC24), which match MAME's three 8254 and three 8253 timers; MF6CN-50 switched-capacitor filters (one per voice, IC109-IC809, plus IC7); 74HC670 register files per voice.
- **[documented]** MIDI implementation chart (version 1.0): receives on channel 1 by default, 1-16 changeable; modes 1-4; note numbers 0-127 (true voice 24-96); pitch bend, CC 1 (modulation), CC 64 (sustain), channel aftertouch, program change 1-127, all notes off (123); System Exclusive sent and received with manufacturer ID 47h. Clock, song position and active sensing are not used.
- **[documented]** The panel buttons are PLAY, REC, EDIT SAMPLE, EDIT PROGRAM, MIDI, UTILITY, DISK and MASTER TUNE, with a numeric keypad, ON/+ and OFF/-, ENT, cursor and PAGE keys, and a CONTROL encoder.
- **[documented]** The OS EPROM part (27C256, 32 KiB) agrees with the 32 KiB chip files of every known S950 set ([../firmware.toml](../firmware.toml)).
- **[open]** The memory map, I/O decode and interrupt wiring are drawn on the schematics, which have not been read here.

## Evidence

- All claims are read from scans of Akai's S950 service manual and operator's manual as hosted on s950fx.com, downloaded 2026-11-13. The IC9 part number was read from a 300 dpi render of page 13: uPD72066C, as in MAME.
- Nothing here was checked on a machine.

## Open questions

- [Akai S950: the first things to establish](../questions/first-steps.md)
