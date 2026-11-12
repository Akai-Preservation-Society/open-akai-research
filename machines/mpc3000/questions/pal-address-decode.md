---
id: mpc3000.q.pal-address-decode
title: PAL address decode
machine: mpc3000
area: hardware
status: open
priority: medium
needs: ["document", "hardware"]
summary: Address decoding on the CPU board is done by PAL devices whose equations have not been read.
related: ["mpc3000.memory-and-io-map", "mpc3000.rom-free-space"]
---
# PAL address decode

## What is unknown

IC25, IC29 and IC31 are 18CV8 devices. Their fuse maps are not public. Every address in this section assumes the decode the MAME driver models. Unknown: whether anything else is decoded, including outside the first megabyte of ROM space.

## Why it matters

A wrong assumption about decoding would undermine the memory map and the free-space analysis.

## How to answer it

Read the devices on a real board if they are not protected, or derive the equations from the schematic sheets of the full service manual, which this project has not located.
