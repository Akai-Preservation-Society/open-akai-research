---
id: mpc3000.build-a-floppy-sys
title: "Recipe: build and run your own program from floppy"
machine: mpc3000
area: modding
firmware: ["mpc3000-v3.08", "mpc3000-v3.11", "mpc3000-v3.12", "mpc3000-vailixi-3.50"]
status: hardware
hardware_tested: partial
summary: Step-by-step route for running your own code on an MPC3000 from a floppy .SYS file, with a working minimal program, the rules it must obey, and how to test before touching a machine.
contributors: ["open-akai-research"]
last_verified: 2026-10-01
depends_on: ["mpc3000.floppy-sys-loader", "mpc3000.bios-services", "mpc3000.address-model", "mpc3000.disassembler-pitfalls"]
---

# Recipe: build and run your own program from floppy

The EPROMs are never touched. Remove the disk, power-cycle, and the
machine is back on its EPROM OS. That makes this the route to try first.
What it can and cannot do today is spelled out under "Three routes".

## Claims

- **[hardware]** A program built with [../tools/sysdisk.py](../tools/sysdisk.py) `hello` loads from floppy and prints its text on the LCD of a real MPC3000. The tool reproduces, byte for byte, the 1.44M disk image used for that run (SHA-256 `ce025a0c...8ad59b58`) when given the same text and disk labels; `tests/test_sysdisk.py` checks this.
- **[static]** Rules for the file, all derived in [floppy-sys-loader.md](floppy-sys-loader.md):
  1. Floppy only, root directory, FAT12, extension `SYS`, any 8.3 name, ordinary attributes.
  2. Make it the only `*.SYS` on the disk, or the first in directory order. A bad first SYS stops the machine.
  3. It must be a DOS MZ file whose `e_cp`/`e_cblp` match the real file size and whose header is at least two paragraphs.
  4. Relocations are applied, so never depend on the load segment (`6900` on 3.12 / Vailixi 3.50, `7000` on 3.08 / 3.11). Keep `e_lfarlc` at or below `3Eh`; each relocation costs a disk read.
  5. Image plus uninitialised data plus stack must end below logical `0xF4000`. The loader does not check.
  6. You start with interrupts off, `DS = 0040`, and (unless the header sets one) the BIOS stack. Set your own stack first.
- **[static]** The BIOS stays mapped, so its services are available: `INT 43h` for text on the LCD, `INT 41h` for files, `INT 45h` to load another MZ. See [bios-services.md](bios-services.md). There is no BIOS service for pads, keys, the wheel, sampling, MIDI or SCSI.
- **[static]** The OS itself uses the 80186-level instructions `PUSH imm16`, `LEAVE` and `OUTSW`, so those are safe to emit. Treat any other instruction beyond the 8086 set as untested here. Never emit the bytes `0F E0` or `0F F0` unless you mean `BRKXA`/`RETXA`.
- **[emulator]** Route A below has been demonstrated in MAME on the Vailixi 3.50 reference image only.
- **[hardware]** Route C below has produced feature builds that run on a real MPC3000 (maintainer observation, 2026-10-27; the individual bench steps were not recorded).
- **[open]** The procedure for route A is not in this repository. Route C is described in [os316-extending.md](os316-extending.md).

## Steps

1. **Identify the EPROM OS** of the target machine if you can (`python3 tools/oar.py identify LS.bin MS.bin`). The hello program does not depend on it; anything that calls fixed OS addresses does.
2. **Build the minimal program** and a disk image:

   ```sh
   python3 machines/mpc3000/tools/sysdisk.py hello --text "HELLO FROM RAM" \
       -o build/HELLO.SYS --disk build/hello.img
   ```

3. **Write your own code.** Assemble a flat binary for offset 0 with no relocations (for example `nasm -f bin`), then wrap and check it:

   ```sh
   python3 machines/mpc3000/tools/sysdisk.py wrap mycode.bin -o build/MYCODE.SYS
   python3 machines/mpc3000/tools/sysdisk.py inspect build/MYCODE.SYS
   python3 machines/mpc3000/tools/sysdisk.py disk -o build/mycode.img build/MYCODE.SYS
   ```

   Start from the shape of the hello program in `sysdisk.py`: `CLI`, point `DS` and `SS` at your code segment, set `SP`, `STI`, then work.
4. **Test in an emulator first.** MAME's `mpc3000` driver boots the EPROM OS and the floppy loader. A boot that reaches Play/Record proves nothing by itself, because the EPROM OS reaches it too: make your program show something only it can show.
5. **Run it on the machine** from a real disk or a floppy-drive emulator. Keep a known-good disk at hand. If the screen shows `software bug of type 11h`, the file was rejected: power off, remove the disk, and check it with `inspect`.

## Three routes, and what each can do today

| Route | What it is | State |
|---|---|---|
| **B. Replacement program** | Your own MZ program is the whole system. | Works on hardware for text output. Everything beyond the BIOS services (pads, audio, MIDI, disk formats) needs hardware knowledge this repository does not have yet. |
| **A. Patched EPROM OS running from RAM** | A builder on your computer takes the OS code and data from your own EPROM dump, applies byte patches, and packs them into a `.SYS` file with a small stub. On the machine the stub moves them into the RAM that the third page table puts in their place and re-enters the boot path, so the OS runs from RAM with your changes. | Demonstrated in the emulator for one image. The stub, the re-entry point and the copy ranges are specific to each image and are an [open question](../questions/patched-rom-os-from-ram.md) for the stock OS versions. Such a file contains firmware: share the patch, never the file ([LEGAL.md](../../../LEGAL.md)). |
| **C. Modified OS 3.16** | OS 3.16 is itself a floppy `.SYS` file, so features can be added to it and the result loaded the same way. | Has run on hardware. The image is mapped in [os316-structure.md](os316-structure.md) and the method is in [os316-extending.md](os316-extending.md). Fix the two stock defects in [os316-defects.md](os316-defects.md) first. |

So, honestly: a replacement program can draw text today, and route C lets
you add pages and behaviour to a working OS 3.16 using the routines named
in its symbol table. Anything touching an area 3.16's map does not cover
(see [GAPS.md](../../../GAPS.md)) still needs research first.

## Evidence

- The hello program's 29 code bytes and the MZ and FAT12 layouts are those of the test program run in MAME (2026-09-25) and on a physical MPC3000 (2026-10-01, one run, LCD photographed). See the evidence section of [floppy-sys-loader.md](floppy-sys-loader.md) for the drive-emulator settings.
- The rules are static results from the loader's code in all four examined images.
- Route A: MAME runs on `mpc3000-vailixi-3.50` showed a patched banner string painted by the relocated OS, the OS pages reading back as RAM, normal boot to Play/Record and panel input being handled.
- Route C: maintainer report of feature builds based on OS 3.16 running on a real MPC3000.

## Open questions

- [Running a patched copy of a stock EPROM OS from RAM](../questions/patched-rom-os-from-ram.md)
- [Unmapped areas of OS 3.16](../questions/os316-unmapped.md)
- [Front-panel protocol](../questions/panel-protocol.md)
- [What RAM the BIOS still uses after hand-off](../questions/bios-data-area.md)
