---
id: mpc3000.floppy-sys-loader
title: The ROM floppy loader that runs a .SYS file at power-on
machine: mpc3000
area: boot
firmware: ["mpc3000-v3.08", "mpc3000-v3.11", "mpc3000-v3.12", "mpc3000-vailixi-3.50"]
status: emulator
hardware_tested: partial
summary: At power-on every examined EPROM OS loads the first *.SYS file on a floppy as a DOS MZ executable into RAM and jumps to it. This is the only ROM path that runs code from removable media.
contributors: ["open-akai-research"]
last_verified: 2026-09-25
sources: ["MAME mpc3000 driver (emulator runs)", "M3K316.pdf release notes for OS 3.16 (2005)"]
depends_on: ["mpc3000.address-model", "mpc3000.eprom-layout", "mpc3000.bios-services"]
---

# The ROM floppy loader that runs a .SYS file at power-on

This is how OS 3.16 was delivered in 2005, and it is how you can run your
own code on an MPC3000 without touching the EPROMs. The working
procedure is in [build-a-floppy-sys.md](build-a-floppy-sys.md); this file
is the evidence underneath it.

## Claims

### The path

- **[static]** After the BIOS starts the OS, the OS prints `Searching floppy for startup files...`, tests whether a floppy is ready, and if so calls its startup-file loader with argument 0 (floppy). Later it does the same for SCSI with argument 1.
- **[static]** For the floppy only, the loader first looks for a file matching `????????` with extension `SYS` in the root directory. If one is found it calls the hand-off routine, which does not return when the file loads. The SCSI pass has no SYS step.
- **[static]** If no SYS is found, the loader goes on to startup `APS`, `PGM` (up to 24, floppy only) and `ALL` files.
- **[static]** The hand-off routine masks interrupts, moves the stack to `0040:69C4`, executes `INT 10h` (which loads the third page table, turning the OS code range into RAM: see [address-model.md](address-model.md)), sets `ES` to the load segment, executes `INT 45h` (the BIOS MZ loader) and far-jumps to the loaded program. If `INT 45h` fails it executes `INT 11h` forever, which paints `System Error ... software bug of type 11h`.
- **[emulator]** With an OS 3.16 floppy, 3.08, 3.11, 3.12 and Vailixi 3.50 all load it and reach its Play/Record screen. With no floppy the SCSI search runs and the EPROM OS continues.
- **[emulator]** The file name does not matter: any 8.3 name with extension `SYS` is taken. Only the first SYS in directory order is opened. If that file is not a valid MZ the machine stops on the type 11h error; it does not try the next file or fall back to the EPROM OS.
- **[hardware]** OS 3.16 and a 288-byte test program have each been loaded and run this way on a physical MPC3000 fitted with a floppy-drive emulator.

### Where things are in each image

- **[static]** Addresses of the path in each examined image (also in [../symbols/](../symbols/)):

  | | 3.08 | 3.11 | 3.12 | Vailixi 3.50 |
  |---|---|---|---|---|
  | OS entry | `B6ED:0000` | `B000:0074` | `B000:0074` | `B000:00DF` |
  | Floppy-ready test | `B6ED:0355` → `F0B9:0442` | `B000:034E` → `E828:0442` | `B000:034E` → `E7F0:0438` | `B000:03B4` → `E7F5:0440` |
  | Startup-file loader | `B6ED:0148` | `B000:0141` | `B000:0141` | `B000:01A7` |
  | SYS hand-off | `FB93:0064` | `FB93:005A` | `FB93:005C` | `FB93:0066` |
  | Load segment | **`7000`** | **`7000`** | `6900` | `6900` |
  | `INT 45h` MZ loader | `F800:013D` | `F800:0143` | `F800:0143` | `F800:0143` |
  | Initialised data (linear) | `0x30000` | `0x20000` | `0x20000` | `0x20000` |
  | Third page table (linear) | `0x7AD29` | `0x7ADCF` | `0x7ADCF` | `0x7ADCF` |

- **[static]** The loader has the same 217 instructions in all four, and the 468 bytes of the `INT 45h` loader are identical in all four (SHA-256 `8edaf657...beb2ef31`).

### What the MZ loader does (`INT 45h`: `DS:DX` = file name, `ES` = load segment)

- **[static]** It reads the first `1Ch` header bytes and requires the signature `MZ` (`4D 5A`). `ZM` is rejected.
- **[static]** It skips the rest of the header (`e_cparhdr × 16 − 1Ch` bytes), then reads the image, whose size is `(e_cp − (e_cblp ≠ 0)) × 512 + e_cblp − e_cparhdr × 16`, to the load segment in 16 KiB chunks.
- **[static]** If `e_crlc` is not zero it reopens the file, reads `e_lfarlc` bytes into a fixed buffer at `0040:642B` **with no bound**, then reads and applies each 4-byte relocation (`word[(seg + load):off] += load`), one disk read per relocation.
- **[static]** It ignores `e_minalloc`, `e_maxalloc`, `e_csum` and `e_ovno`, does not support overlays, and does **not** check that the image fits in memory.
- **[static]** It returns the entry point and stack from the header; error codes are `AH` = 1 short header, 2 bad signature, 3 short header skip, 4 short image.

### The machine state your program starts in

- **[static]** State at the first instruction:

  | Item | Value |
  |---|---|
  | `CS:IP` | `(load + e_cs) : e_ip` |
  | `SS:SP` | `(load + e_ss) : e_sp`; if both header fields are 0, the BIOS stack `0040:69C4` is kept |
  | `DS` | `0040` |
  | `ES` | same as `CS` |
  | Interrupt flag | 0 (disabled) |
  | Addressing | XA=1, third page table |
  | Vector 8 | points at a small BIOS-range handler (`INT 42h`, write `60h` to port `C010h`, `IRET`) |

- **[static]** Memory under the third table: logical `0x00000-0xF3FFF` is RAM, `0xF4000-0xF7FFF` is the NVRAM window, `0xF8000-0xFFFFF` is still the BIOS, kernel and boot ROM. **The EPROM OS code is no longer mapped.** A loaded program is a whole replacement for it unless it copied what it needs first.
- **[static]** The image is loaded at logical `0x69000` (3.12, Vailixi 3.50) or `0x70000` (3.08, 3.11). RAM is contiguous up to `0xF3FFF`, leaving 569,344 bytes (from `0x69000`) or 540,672 bytes (from `0x70000`) for image, uninitialised data and stack.
- **[static]** During the load the BIOS uses `0040:63EC-0040:6DC4` (header copy, file name, relocation buffer, stack).
- **[open]** What happens if a program writes into the NVRAM page at `0xF4000`, and whether that can upset the EPROM OS on the next power-on.

### Disk format

- **[static]** The BIOS mounts a FAT12 volume. It copies the 21-byte BIOS parameter block, requires 1-32 heads and 1-20 sectors per track, then picks one of three built-in geometries by sectors per track: 9 (720K), 10 (800K) or 18 (1.44M).
- **[static]** Directory entries with attribute bits `1Eh` set (hidden, system, volume label, directory) are skipped. `?` in the pattern matches any character.
- **[emulator]** A plain 1.44M FAT12 image loads. 720K and 800K images were not tried.
- **[hypothesis]** The floppy-ready test waits in a loop that has no timeout of its own, then reads a status byte and tests bit `20h`, which would be the "ready" bit of a µPD765-family controller.

## Evidence

- **Static.** The path was decoded from the linear images with a V53-aware instruction decoder and pinned: addresses, strings, instruction counts and routine hashes were checked in all four images (2026-09-25). The first bytes of each routine and the whole `INT 45h` loader are in [../pins/](../pins/); they were re-checked against the four dumps on 2026-11-13.
- **Emulator.** MAME `mpc3000`, one run per row:

  | Floppy contents (root order) | EPROM OS | Result at 30 s |
  |---|---|---|
  | `M3K316.SYS` | 3.08, 3.11, 3.12, 3.50 | OS 3.16 banner, then Play/Record |
  | The same file renamed | 3.50 | OS 3.16 loads |
  | Valid SYS, then a non-MZ SYS | 3.50 | OS 3.16 loads; the second file is never opened |
  | Non-MZ SYS, then a valid SYS | 3.50 | `software bug of type 11h`, permanently |
  | A text file only | 3.50 | SCSI search, EPROM OS continues |
  | 288-byte test program | 3.50 | its text appears on the LCD |
  | No floppy | 3.50 | SCSI search, no loader call |

- **Hardware.** 2026-10-01, one physical MPC3000 with a FlashFloppy drive emulator serving a 1.44M image (`interface = ibmpc-hdout`, `pin34 = rdy`, `host = akai`): the 288-byte test program's text appeared on the LCD (photographed), and OS 3.16 loaded on the same machine. The unit's EPROM OS reported version 3.50. The run on real 3.08, 3.11 and 3.12 EPROMs has not been made.
- The OS 3.16 release notes say it needs EPROM OS 3.11 or later. In the emulator 3.08 loads it too; the reason for the stated requirement is unknown.

## Open questions

- [Real floppy drives, and 720K / 800K disks](../questions/real-drives-and-other-disk-sizes.md)
- [NVRAM layout and what a RAM program may do to it](../questions/nvram-layout.md)
- [What RAM the BIOS still uses after hand-off](../questions/bios-data-area.md)
- [OS 3.10 has not been examined](../questions/os-3.10-image.md)
