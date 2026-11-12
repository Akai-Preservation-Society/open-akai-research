---
id: mpc3000.os316-extending
title: "Recipe: add code to OS 3.16 and load it from floppy"
machine: mpc3000
area: modding
firmware: ["mpc3000-v3.16-sys"]
status: hardware
hardware_tested: partial
summary: Append a code segment to M3K316.SYS, extend its relocation table, move the new code above 3.16 at load time, and hook 3.16 by far jumps. Builds made this way run on real hardware.
contributors: ["open-akai-research"]
last_verified: 2026-10-22
depends_on: ["mpc3000.os316-structure", "mpc3000.os316-defects", "mpc3000.floppy-sys-loader", "mpc3000.build-a-floppy-sys"]
---

# Recipe: add code to OS 3.16 and load it from floppy

This is "route C" in [build-a-floppy-sys.md](build-a-floppy-sys.md). The
EPROMs are untouched and the result runs on any examined EPROM OS. The
modified file contains 3.16, so share a builder or a patch manifest, not
the file ([LEGAL.md](../../../LEGAL.md)).

No builder is published here yet. The steps describe one that has worked.

## Claims

- **[hardware]** A 3.16 build made this way, with about 12 KB of added code hooked into several pages, loaded and passed a 40-minute functional checklist on a physical MPC3000 (Vailixi 3.50 EPROM, `L = 6900h`).
- **[emulator]** The same builds boot and pass the same tests on the 3.12, Vailixi 3.50, 3.11 and 3.08 sets in MAME.
- **[static]** The memory available for added code is above 3.16's extent and below page 61: logical `L × 16 + 7E000h` to `F3FFFh`. That is `D000h` (53,248) bytes when `L = 6900h` and `6000h` (24,576) bytes when `L = 7000h`.
- **[static]** RAM above 3.16's extent is not used by 3.16, except by the SCSI reader's stack wrap, which must be fixed first ([os316-defects.md](os316-defects.md)).
- **[emulator]** No access to that range by 3.16 was seen in 355 seconds of heavy use on all four sets, with the SCSI fix in place.
- **[static]** Code that has to be the same on every EPROM can move a `L = 7000h` load down to `L = 6900h` before 3.16 starts: re-apply every relocation with `−700h`, copy the image down, and correct the two places the loader recorded `L` (`0040:640A` and `0040:68C2`). Then 3.16 and the added code run at the same addresses on every set.
- **[emulator]** With that move, memory and registers at 3.16's entry were identical for `L = 6900h` and `L = 7000h`. The move took 113 ms of emulated time on the 3.08 and 3.11 sets.
- **[open]** The move has not been run on real 3.08 or 3.11 EPROMs. See [the question](../questions/os316-on-other-eproms.md).

## Steps

1. **Start from the exact file.** Check `M3K316.SYS` with `python3 tools/oar.py identify` and refuse any other bytes.
2. **Assemble the added code at offset 0** as one segment ("the cave"). Every segment word it contains (far calls into 3.16, references to `DGROUP 609Ch`, the cave's own segment) must be listed so it becomes an MZ relocation.
3. **Append the cave to the load image** at relative paragraph `6834h` (the end of the image). That spot is inside 3.16's uninitialised data, which 3.16 zeroes at start-up, so it is only a staging area.
4. **Pick a home** at relative paragraph `7E00h` or higher, above 3.16's extent (`7DFBh`). Check that home plus cave size stays below logical `F4000h` for every `L` you support, and halt rather than continue if it would not.
5. **Point the MZ entry at a small routine in the cave** that copies the cave to its home and then far-jumps to 3.16's entry `L:0000`. Because the cave is assembled at offset 0, it runs identically in both places. Do not use the stack during this routine: the loader's stack top lies inside the staged cave once the cave is longer than about `841Eh` bytes.
6. **Apply the two memory fixes** in the same routine: set the pool end at image `48535h`, and install the SCSI reader wrapper ([os316-defects.md](os316-defects.md)).
7. **Hook 3.16** by replacing instructions with a far jump or call into the cave (`EA` or `9A` with the cave's segment, relocated). Remove any existing relocation that falls inside the bytes you replace. Check the original bytes at every hook before patching.
8. **Extend the relocation table.** 794 entries fit in the existing header; beyond that the header must grow. Update `e_cp`/`e_cblp`, `e_crlc` and, if the header grows, `e_cparhdr`.
9. **Check the file** with `machines/mpc3000/tools/sysdisk.py inspect`, simulate the loader at both load segments, then test in MAME on several EPROM sets before hardware.

## Evidence

- **Hardware.** 2026-10-06, one physical MPC3000 (Vailixi 3.50 EPROM, about 32 MB sound memory), a floppy-drive emulator, a seven-gate checklist covering boot, new pages, sound editing, pad behaviour, sequence memory, save and load, and stability. All gates passed; photos and a boot video kept by the contributor. A larger build was later run on the same unit.
- **Emulator.** MAME `mpc3000`, 2026-10-05 to 2026-10-22: a 62-byte probe cave first, then full builds; release runs of up to 242 automated tests per build across the four EPROM sets, one execution each.
- **Static.** Memory limits and relocation counts from the file and the builds; the stack hazard in step 5 was found by running the cave's entry routine in an x86 interpreter against a model of the loader.

## Open questions

- [Unmapped areas of OS 3.16](../questions/os316-unmapped.md)
- [NVRAM layout and what a RAM program may do to it](../questions/nvram-layout.md)
