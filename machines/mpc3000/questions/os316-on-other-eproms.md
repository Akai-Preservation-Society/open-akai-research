---
id: mpc3000.q.os316-on-other-eproms
title: OS 3.16 builds on real 3.08, 3.11 and 3.12 EPROMs
machine: mpc3000
area: boot
status: open
priority: medium
needs: ["hardware"]
summary: Stock and modified OS 3.16 have run on hardware only on a machine with a Vailixi 3.50 EPROM. The other EPROM versions, and the load-segment move, are emulator results.
related: ["mpc3000.os316-extending", "mpc3000.os316-defects"]
---

# OS 3.16 builds on real 3.08, 3.11 and 3.12 EPROMs

## What is unknown

Whether, on physical machines with Akai 3.08, 3.11 or 3.12 EPROMs:

- stock 3.16 shows the sequence-pool defect (expected on 3.12, not on 3.08 or 3.11);
- a build with the pool fix reports the expected free sequence memory;
- a build that moves a `L = 7000h` load to `6900h` boots (3.08, 3.11).

## Why it matters

Most MPC3000s carry 3.11 or 3.12. Every claim that a 3.16 build "runs on any
MPC3000" rests on this.

## How to answer it

Identify the EPROMs by hash first (`oar.py identify`). Boot stock 3.16, record
the free sequence memory on the System Information page, record 30 seconds,
press Song, and note whether the machine responds. Repeat with a fixed build.
Photograph the screens and record the results in the findings.
