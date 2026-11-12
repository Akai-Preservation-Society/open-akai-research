---
id: mpc2000xl.q.panel-commands
title: Commands from the main CPU to the panel
machine: mpc2000xl
area: panel
status: open
priority: low
needs: ["analysis", "hardware"]
summary: The panel MCU has a receive handler, so the main CPU can send it commands, but none are documented.
related: ["mpc2000xl.panel-protocol", "mpc2000xl.boot-and-panel-handshake"]
---

# Commands from the main CPU to the panel

## What is unknown

Known: the panel sends reports with headers `80`-`AF` and `FF`, and the ID `E0 11` at power-on. Unknown: whether the main CPU ever sends anything to the panel, the command format, and the panel's scan timing and pad sensitivity settings.

## Why it matters

Pad sensitivity or scan changes would need it.

## How to answer it

Disassemble the panel EPROM's receive handler (`0x027A`) and its main loop; on the main side, look for writes to the panel link. Confirm with a logic analyser on the link.
