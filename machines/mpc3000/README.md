# Akai MPC3000

Entry point for everything known here about the MPC3000 (1994). Facts
that fit on a line are in [machine.toml](machine.toml); known firmware
images are in [firmware.toml](firmware.toml).

## What you can do today

| You want to | State | Read |
|---|---|---|
| Know which OS image a machine or a dump holds | Works: five EPROM OS images and one floppy OS are identified by hash | [findings/eprom-layout.md](findings/eprom-layout.md) |
| Run your own program on the machine without changing it | Works, run on real hardware: a floppy `.SYS` file loaded into RAM at power-on | [findings/build-a-floppy-sys.md](findings/build-a-floppy-sys.md) |
| Put text on the LCD from your program | Works, run on real hardware | [findings/bios-services.md](findings/bios-services.md) |
| Read a file from floppy in your program | Described from the code; not exercised outside the ROM's own loader | [findings/bios-services.md](findings/bios-services.md) |
| Understand any address in the firmware | Documented | [findings/address-model.md](findings/address-model.md) |
| Plan an EPROM modification | Free space and its catch are documented; nobody has burned one from this information | [findings/rom-free-space.md](findings/rom-free-space.md) |
| Add pages or behaviour to the OS, from floppy | Works, run on real hardware: extend OS 3.16, using its 111 named routines | [findings/os316-extending.md](findings/os316-extending.md), [findings/os316-structure.md](findings/os316-structure.md) |
| Run stock OS 3.16 safely on 3.12 / 3.50 EPROMs | Two defects found, with fixes | [findings/os316-defects.md](findings/os316-defects.md) |

## What you cannot do yet from this repository

Each line is an open question with a plan for answering it.

| You want to | Missing | Question |
|---|---|---|
| Change parts of OS 3.16 that are not mapped | Names for the sequencer, MIDI and most disk code in 3.16 | [os316-unmapped](questions/os316-unmapped.md) |
| Patch a stock EPROM OS and run it from RAM | The stub details for 3.08, 3.11 and 3.12 | [patched-rom-os-from-ram](questions/patched-rom-os-from-ram.md) |
| Change behaviour on a 3.11 or 3.12 machine by patching | Named routines for those images | [stock-os-code-map](questions/stock-os-code-map.md) |
| React to pads, keys or the wheel | The panel protocol | [panel-protocol](questions/panel-protocol.md) |
| Play, record or process audio | The sample engine | [sample-engine-dsp](questions/sample-engine-dsp.md) |
| Touch sequences or timing | The sequencer's data model | [sequencer-model](questions/sequencer-model.md) |
| Draw graphics | The LCD controller's graphic mode | [lcd-controller-commands](questions/lcd-controller-commands.md) |
| Read or write the machine's files on a computer | File formats | [disk-file-formats](questions/disk-file-formats.md) |
| Add MIDI behaviour | MIDI handling | [midi-handling](questions/midi-handling.md) |

The full list, with priorities, is in [../../GAPS.md](../../GAPS.md).

## Reading order

1. [findings/hardware-overview.md](findings/hardware-overview.md): the chips.
2. [findings/memory-and-io-map.md](findings/memory-and-io-map.md): where they sit. Tables in [hardware/](hardware/).
3. [findings/eprom-layout.md](findings/eprom-layout.md): the firmware image and how to identify it.
4. [findings/address-model.md](findings/address-model.md): **required** before using any address.
5. [findings/disassembler-pitfalls.md](findings/disassembler-pitfalls.md): **required** before reading any code.
6. [findings/floppy-sys-loader.md](findings/floppy-sys-loader.md) and [findings/build-a-floppy-sys.md](findings/build-a-floppy-sys.md): running your own code.
7. [findings/bios-services.md](findings/bios-services.md), [findings/interrupt-vectors.md](findings/interrupt-vectors.md), [findings/calling-conventions.md](findings/calling-conventions.md): what your code can call, and how the OS is put together.
8. [findings/os316-structure.md](findings/os316-structure.md), [findings/os316-defects.md](findings/os316-defects.md), [findings/os316-extending.md](findings/os316-extending.md): OS 3.16, the base for floppy-delivered features.
9. [findings/rom-free-space.md](findings/rom-free-space.md): for EPROM work.

## Firmware images

| Id | What | Examined here |
|---|---|---|
| `mpc3000-v3.08` | Akai OS 3.08, EPROM pair | Boot path and loader |
| `mpc3000-v3.10` | Akai OS 3.10, EPROM pair | No |
| `mpc3000-v3.11` | Akai OS 3.11, EPROM pair | Boot path, loader, page tables |
| `mpc3000-v3.12` | Akai OS 3.12, EPROM pair | Boot path, loader, page tables |
| `mpc3000-vailixi-3.50` | Vailixi OS 3.50 (independent developer), reference dump | Most code-level findings |
| `mpc3000-v3.16-sys` | OS 3.16 maintenance upgrade (independent developer), floppy file | Structure, two defects, 111 symbols |
| `mpc3000-panel-v1.0` | Front-panel microcontroller program | Identified only |

Most code-level findings were made on the Vailixi 3.50 reference dump
because that is where the first contributor worked. They are keyed to
that image and must not be assumed for another. Machines that report
"3.50" on screen do not all hold the reference dump: identify by hash.

## Tools

- [tools/sysdisk.py](tools/sysdisk.py): build, check and pack floppy `.SYS` programs.
- [symbols/](symbols/): named addresses per image (for `mpc3000-v3.16-sys`, file offsets are into the `.SYS` file). [pins/](pins/): byte-range hashes; run `python3 tools/oar.py verify <id> <linear image>`.

## Emulation

MAME has an `mpc3000` driver. Its author marks it as not working, but it
boots the EPROM OS to the main screen and runs the floppy loader, which
is enough to test much of what is described here. Remember that the CPU
core runs at 16 MHz on the real machine.
