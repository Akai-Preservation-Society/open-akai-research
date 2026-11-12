---
id: mpc3000.q.lcd-controller-commands
title: LCD controller commands and graphics
machine: mpc3000
area: display
status: open
priority: medium
needs: ["document", "analysis", "hardware"]
summary: The text path to the LCD is known. The controller command set as wired on this board, the graphic mode, and four of the eight INT 43h functions are not.
related: ["mpc3000.bios-services"]
---
# LCD controller commands and graphics

## What is unknown

Unknown: an LC7981 datasheet-level description of the commands the BIOS sends; what `INT 43h` functions 3 and 6 do and what 2, 5 and 7 are for in practice; how the OS draws graphics (waveforms, mixer pages); the display's pixel dimensions and the memory layout in graphic mode; contrast control.

## Why it matters

Any feature with a custom screen needs to draw. Text alone is available today.

## How to answer it

Obtain the LC7981 or HD61830 datasheet and annotate the BIOS's port writes against it. In the emulator, log writes to ports `0x00E0`/`0x00E2` while the OS draws a waveform. Photograph a real LCD to confirm.
