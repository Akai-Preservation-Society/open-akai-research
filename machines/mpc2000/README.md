# Akai MPC2000

Entry point for the MPC2000 (Classic). Facts are in
[machine.toml](machine.toml); the OS files are identified by hash in
[firmware.toml](firmware.toml). Every code-level finding is for **OS 1.72**
(`mpc2000-v1.72-exe` and `mpc2000-v1.72-sys`).

Most of what is here comes from a published mod pack's source (vubeatz,
`mpc2000_2000xl_mod_pack`), restated as facts. Each address was checked
against the stock 1.72 bytes and pinned. What a routine does, and its
arguments, is `documented` from that source and has **not** been run
here, on hardware or in an emulator. Nothing recorded for the MPC2000XL may
be assumed to hold for this machine, even where names match.

## What you can do today

| You want to | State | Read |
|---|---|---|
| Find an address in your copy of the OS | Formulas checked against the bytes | [findings/os-files.md](findings/os-files.md) |
| Draw on screen, bind keys, stop voices, edit values | Routines and INTs named, arguments from a mod source | [findings/os-services.md](findings/os-services.md) |
| Read or change programs, note parameters, sequences | In-RAM layouts | [findings/program-and-voice-data.md](findings/program-and-voice-data.md) |
| Read, write or list files on floppy or SCSI | INT 2Ch / 2Dh services | [findings/filesystem.md](findings/filesystem.md) |

## What you cannot do yet from this repository

| You want to | Missing | Question |
|---|---|---|
| Know how the OS is loaded, and undo a change safely | Boot and load path | [os-load-path](questions/os-load-path.md) |
| Rely on any hardware fact | Hardware, memory and I/O maps | [first-steps](questions/first-steps.md) |

## Reading order

1. [findings/os-files.md](findings/os-files.md): **required** before using any address.
2. [findings/os-services.md](findings/os-services.md), [findings/program-and-voice-data.md](findings/program-and-voice-data.md), [findings/filesystem.md](findings/filesystem.md).
3. [symbols/](symbols/) and [pins/](pins/). Check your files: `python3 tools/oar.py verify mpc2000-v1.72-sys MPC2000.SYS` and `python3 tools/oar.py verify mpc2000-v1.72-exe MPC2000.EXE`.

## Outside this repository

Manuals, emulators, tools and mods: [../../docs/external-resources.md](../../docs/external-resources.md).
