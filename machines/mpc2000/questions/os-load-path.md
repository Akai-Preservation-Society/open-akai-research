---
id: mpc2000.q.os-load-path
title: How OS 1.72 is loaded and where it runs
machine: mpc2000
area: boot
status: open
priority: high
needs: ["analysis", "document", "hardware"]
summary: How the boot ROM starts MPC2000.EXE, where the EXE and SYS sit in physical memory, and how a modified SYS can be loaded and undone, are not established.
related: ["mpc2000.os-files", "mpc2000.q.first-steps"]
---

# How OS 1.72 is loaded and where it runs

## What is unknown

Known: the OS is two MZ files; the SYS runs at segment `3000` and the EXE's segments are `0000`, `0FE8` and `1F31` relative to its load point (documented from a mod source, with file-offset formulas checked statically; see [../findings/os-files.md](../findings/os-files.md)). The EXE contains the names of both files.

Unknown: what code reads `MPC2000.EXE` from the floppy at power-on (a boot ROM, or the panel side), where the EXE is placed in physical memory, whether page registers are used, what the EXE does to load the SYS, and what happens if either file is missing or modified.

## Why it matters

A safe, undoable way to run changed code depends on it. The mod source changes only the SYS on disk and patches the EXE in RAM. That suggests a floppy carrying a modified SYS is enough, but it has not been checked here.

## How to answer it

Dump the main-board boot ROM (if any) and identify it by hash. Trace the EXE's loader statically from its MZ entry point, looking for the `MPC2000.SYS` string at file `0x107D5` and its users. Then boot a stock unit from a floppy holding stock files and an unmodified copy of each, and record what happens.
