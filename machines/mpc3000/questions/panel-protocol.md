---
id: mpc3000.q.panel-protocol
title: Front-panel protocol (pads, keys, data wheel)
machine: mpc3000
area: panel
status: open
priority: high
needs: ["firmware-image", "analysis", "hardware"]
summary: How the panel microcontroller reports pads, keys and the wheel to the main CPU, and what the main CPU sends back, is not documented.
related: ["mpc3000.memory-and-io-map", "mpc3000.interrupt-vectors"]
---
# Front-panel protocol (pads, keys, data wheel)

## What is unknown

The panel µPD78C10 runs its own 32 KiB program (identified by hash in `firmware.toml`, not analysed). Its serial output reaches UART receivers 3 and 4 on the main board. Unknown: the message format in each direction, how pad velocity and pressure are encoded, how the wheel is reported, baud rate and framing, and what the OS does with each message.

## Why it matters

A replacement program cannot read a pad or a key without it, and no feature that reacts to the panel can be added to the OS without knowing where panel messages are handled.

## How to answer it

Disassemble the panel EPROM (µPD78C10 instruction set) from its reset vector; find the serial transmit routine and the tables it sends. On the main CPU side, find the handlers for the UART receive interrupts and follow the bytes. Confirm by capturing the serial line on a real machine with a logic analyser while pressing each control.
