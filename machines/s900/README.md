# Akai S900

Seed coverage: hardware facts, a memory map, an I/O port map and the hashes of the ROM images MAME knows (OS 1.2a and 1.2c), all taken from MAME's driver source. The S900 boots later OS versions from floppy, so a disk-loaded route for your own code probably exists, but it has not been studied.

Findings: [hardware-overview](findings/hardware-overview.md) (Akai's documents), [rom-images](findings/rom-images.md) (which chip set you have) and [boot-disks](findings/boot-disks.md) (loading an OS from floppy). Nothing has been checked on hardware or in a
working emulator here. Nothing recorded for another machine may be assumed to
hold for this one, even where the two share a CPU or a file format.

## What is here

- [machine.toml](machine.toml): one-line facts, each with its source.
- [hardware/memory-map.csv](hardware/memory-map.csv) and [hardware/io-ports.csv](hardware/io-ports.csv): from MAME's driver.
- [firmware.toml](firmware.toml): known images by chip CRC32 and SHA-1. Check your own dump with `python3 tools/oar.py identify`.
- [questions/first-steps.md](questions/first-steps.md): what to establish next.

## Outside this repository

Manuals, emulators, tools and free mods for this machine are listed in
[../../docs/external-resources.md](../../docs/external-resources.md).

To contribute, read [../../CONTRIBUTING.md](../../CONTRIBUTING.md), and
see [../mpc3000/](../mpc3000/README.md) for an example of a section with
content.
