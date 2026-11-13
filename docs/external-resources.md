# External resources

What exists outside this repository: documentation, emulators, tools, and
free firmware mods for Akai MPCs and rack samplers. Last checked
2026-11-13.

Nothing here has been verified by this project unless a finding says so.
Treat every fact taken from these sources as evidence class `documented`
(see [evidence.md](evidence.md)) and cite the source when you use it.
Links point to the original publishers. This repository does not copy
their files; see [../LEGAL.md](../LEGAL.md).

"Open source" below means the source code is published under a licence
that allows reuse. "Free" means no charge. Several of the best-known mods
are free but closed: you can use them, but you cannot read or reuse how
they work.

## Emulators

| Project | Machines | Licence | Notes |
|---|---|---|---|
| [MAME](https://github.com/mamedev/mame) `src/mame/akai/` | MPC60 (and with Marion Systems SCSI board), MPC2000XL, MPC3000, S900, S950 (and with SCSI), S1000, S1000PB, S1100, S2000, S3000, CD3000i, S3000XL, CD3000XL | BSD-3-Clause for these drivers | Every one is flagged `MACHINE_NOT_WORKING`. The driver sources are the best public description of each board's memory map, I/O ports and chips, and of which ROM images exist (by CRC32 and SHA-1). Read at commit `c2caa8969adb` (2026-11-13). |
| [vMPC2000XL](https://github.com/izzyreal/vmpc-juce) (izzyreal) | MPC2000XL | GPL-3.0 | A re-implementation of the 2000XL's behaviour as a standalone app and plugin, not an emulation of its CPU. Useful for file formats and screen logic; it runs no Akai code. Core library: [izzyreal/mpc](https://github.com/izzyreal/mpc). |
| [mpc2000-emulator](https://github.com/dariuszchynek/mpc2000-emulator) (vubeatz) | MPC2000 (Classic) | BSD-3-Clause (LICENSE file; GitHub shows "Other") | Experimental, built as its own MAME target (`mpc2000cdiag`, MAME pinned at commit `774a180df2b6`). Runs the original V53 code from your unmodified OS 1.72 `MPC2000.EXE` (it checks the SHA-256 recorded in [../machines/mpc2000/firmware.toml](../machines/mpc2000/firmware.toml)) plus a boot floppy holding `MPC2000.SYS`. Skips the boot ROM through a "diagnostic EXE handoff" and approximates the panel MCU with serial messages. Its author reports booting to MAIN on macOS Apple Silicon. Audio is off and SCSI has no disks. No firmware is included. Read 2026-11-13. |
| [mpc2000xl-emulator](https://github.com/dariuszchynek/mpc2000xl-emulator) (vubeatz) | MPC2000XL | BSD-3-Clause (LICENSE file; GitHub shows "Other") | Experimental MAME target (`mpc2000xldiag`, same pinned MAME) derived from the Classic one. Loads the stock OS 1.20 `MPC2KXL.BIN` (SHA-256 as `mpc2000xl-os1.20` here) into the ROM map and starts at the native reset vector, so the guest boot ROM runs. The panel MCU is approximated. Its author reports reaching MAIN with working Open Window, Next Sequence, Track Mute and bank LEDs on macOS Apple Silicon. Floppy load/save, audio and MIDI are not implemented or not verified. No firmware is included. Read 2026-11-13. |

## Per machine

### Akai MPC60 / MPC60-II

- MAME driver `mpc60.cpp`: 80186 at 10 MHz, uPD72066 floppy controller, LC7981-class LCD controller (emulated as an HD61830), two MB89371 UARTs, uPD78C11 panel CPU, L4003 sound DSP, optional NCR5380 SCSI. Memory and I/O maps are recorded in [../machines/mpc60/hardware/](../machines/mpc60/hardware/).
- [Operator's manual for software version 3.1](https://www.polynominal.com/akai-mpc60/akai-mpc60-manual.pdf), by Roger Linn and David Battino (Roger Linn Design).
- [Service manual on ManualsLib](https://www.manualslib.com/manual/997884/Akai-Mpc-60.html), including the memory expansion board.
- [Roger Linn Design: version 3.10 overview](https://www.rogerlinndesign.com/support/support-3-10-overview) and [FAQ](https://www.rogerlinndesign.com/support/support-mpc-3-10-faqs). Version 3.10 brings MPC3000 software features to the MPC60 and also installs in the ASQ10. The FAQ links a free MIDI file conversion utility.

### Akai MPC2000 (Classic)

- [Operator's manual (PDF, mpcstuff.com)](https://www.mpcstuff.com/content/MPC_Manuals/MPC2000_manual.pdf); addenda for [version 1.3](https://cf3.zzounds.com/media/MPC20V13-5843a37bf1a7835cf07cc2c1a5f83d22.PDF) and [version 1.5](https://cf3.zzounds.com/media/MPC2V150-88474e78de33e4e6e88bc2b2374cf6e5.PDF).
- [Sweetwater: OS update instructions](https://www.sweetwater.com/sweetcare/articles/upgrade-os-of-akai-mpc2000/). An update ships as two files, `mpc2000.exe` and `mpc2000.sys`, copied to a DOS-format floppy.
- Final OS: 1.72 ([Gearnews](https://www.gearnews.com/?p=261343)).
- MAME's `mpc2000.cpp` header describes the MPC2000 and 2000XL together as a cost-reduced MPC3000 (NEC V53, uPD72068 floppy controller, MB89352 SCSI optional on the 2000, LC7981 LCD, uPD78C10 panel CPU, L7A1045 DSP), but defines only the 2000XL. Nothing in it has been checked against a 2000 Classic.
- A short service manual (16 pages) is listed on ManualsLib alongside the MPC60 manual above.

### Akai S900 and S950

- MAME driver `s900.cpp` covers both: NEC V30, uPD7265 (S900) or uPD72066 (S950) floppy controller, uPD71071 DMA controllers for sampling and voices, 8253/8254 timers, 8259 interrupt controller, 6850 ACIA for MIDI, 8251 serial port on the S900, 2-line HD44780-class LCD, optional MB89352 SCSI on the S950. Memory and I/O maps are in [../machines/s900/hardware/](../machines/s900/hardware/) and [../machines/s950/hardware/](../machines/s950/hardware/).
- [s2kdie](https://wiw.org/~meta/s2k.php) by Mick Kane: a Linux disk image editor for S900/S2000/S3000 floppies, with S900 OS 4.0 and S2000 OS 2.0 disk images, S900/S950 MIDI SysEx implementation charts, and an S900/S950 RS232 sample transfer program linked from the page.
- [akaiutil](https://sourceforge.net/projects/akaiutil/) supports S900 and S950 floppies and images (see Tools).
- Floppy emulation: [FlashFloppy host settings for Akai](https://github.com/keirf/flashfloppy/wiki/Host-Platforms) (`host = akai`, `interface = akai-s950` for the S950), the [HxC forum thread on the S950](https://hxc2001.com/floppy/forum/viewtopic.php?p=26182), and the [donsolaris.com S950 upgrade series](https://donsolaris.com/?tag=s-950).
- [Akai S900 archive (R-Massive)](https://zine.r-massive.com/akai-s900-archive) for factory disks.

### Akai S3000 family (S2800, S3000, S3200, CD3000i, and the XL models)

- MAME driver `s3000.cpp` covers the S2000, S2800, S3000, CD3000i, S3200, S3000XL, S3200XL and CD3000XL, and defines `s2000`, `s3000`, `cd3000i`, `s3000xl` and `cd3000xl` (no `s3200`): NEC V53A at 32 MHz, uPD72069 floppy controller, MB89352 SCSI, LC7981 LCD (HD44780 on the S2000), L7A1045-L6028 sample DSP, optional IB304F filter and EB16 effects boards (standard on the S3200), MIDI on the V53's serial unit. It gives separate memory and I/O maps for the S3000 board and the XL board, and says the S2000 and S3200 use the XL board. ROM sets: S3000 2.0 and 1.50, CD3000i 2.00 and 1.60, S3000XL 2.00, 1.50 and 1.06, CD3000XL 2.00, S2000 1.5 and 1.0. Its S3000 2.0 set is the image recorded in [../machines/s3200/](../machines/s3200/README.md), with the board conflict noted there.
- The S3000 disk and file formats are also described by [akaiutil](https://sourceforge.net/projects/akaiutil/), [akaitools' S3000 format page](https://lsnl.jp/~ohsaki/software/akaitools/S3000-format.html) and libakai (see Tools). [../machines/s3200/findings/disk-formats.md](../machines/s3200/findings/disk-formats.md) is read from the firmware instead and has not been compared with them.

## Tools

| Tool | What it does | Licence |
|---|---|---|
| [akaiutil](https://sourceforge.net/projects/akaiutil/) (K. M. Indlekofer) | Read and write S900/S950/S1000/S1100/S2000/S2800/S3000/S3000XL/CD3000/S3200 filesystems on disks, images and drives | Source published on SourceForge with its own terms ("special restrictions apply"); read them before reusing code |
| [akaidatdecode](https://sourceforge.net/projects/akaidatdecode/) (same author) | Decode S1000/S3000 DAT backups from a WAV recording into a tar file | As above |
| [s2kdie](https://wiw.org/~meta/s2k.php) (Mick Kane) | S900/S2000/S3000 floppy image editor | See the page |
| akaitools ([usage notes on MPC-Forums](https://www.mpc-forums.com/viewtopic.php?p=1746831)) | Linux tools for S1000/S3000-family hard disks | See the distribution |
| [libgig / libakai](https://svn.linuxsampler.org/svn/web/trunk/www.linuxsampler.org/libakai/README) (LinuxSampler) | C++ library for S1000/S01/S2000/S3000 formats, now part of libgig | GPL |
| [FlashFloppy](https://github.com/keirf/flashfloppy) | Open-source firmware for Gotek floppy emulators, with Akai host support | Open source |

## Free firmware mods, by machine

| Machine | Mod | Author | Free | Source open | How it is applied |
|---|---|---|---|---|---|
| MPC2000, MPC2000XL | [MPC2000 MODS](https://vubeatz.com/mpc-mods.html) | vubeatz | Yes | Source available ([GitHub, PolyForm Noncommercial 1.0.0](https://github.com/dariuszchynek/mpc2000_2000xl_mod_pack), assembly only; not open source, and not usable in this repository except as facts) | An installer patches your own copy of the final Akai OS (1.72 or 1.20) on a computer; you load the result yourself. Version 1.8 in September 2026; 2.0 (October 2026) made each mod selectable and added a "safety meter"; 2.1 (macOS apps, October 2026) added GRID VIEW and, on the Classic, RESAMPLE. The installers accept only the exact stock files, by SHA-256. An experimental option uses larger Gotek images: the bundled blank HFE files have 120 or 240 tracks per side instead of 80, at the normal 500 kbit/s (2.21 and 4.42 MB). The installer's licence is not stated; the source release (November 2026) is PolyForm Noncommercial 1.0.0. Facts from the source release are recorded in [../machines/mpc2000/](../machines/mpc2000/README.md) and [../machines/mpc2000xl/findings/os-services-from-mods.md](../machines/mpc2000xl/findings/os-services-from-mods.md). |
| MPC3000 | [OS 3.16](http://www.mpc3000.com/updated_os.htm) | Rohan Mansell | Yes | No | Floppy-loaded OS. This repository maps it in [../machines/mpc3000/](../machines/mpc3000/README.md). |
| MPC3000 | [OS 3.41 Track Mute Edition](https://www.deep88.com/vibecod/) | Deep88 | Yes (never to be sold, per its README) | No | Floppy-loaded OS (SYS, IMG and HFE), November 2026. Track Mute page, sampling and chopping tools, mute groups and more. Built on OS 3.16: see [../machines/mpc3000/findings/tme341-structure.md](../machines/mpc3000/findings/tme341-structure.md). |
| S900 | [S900FX](https://s900fx.com) | Mike Feedback | Yes | Not stated | Custom OS that turns the sampler into a real-time 12-bit processor. |
| S950 | [S950FX](https://s950fx.com) | Mike Feedback | Yes | Not stated | As above, for the S950. |
| S900 | OS 4.0 disk ([via s2kdie](https://wiw.org/~meta/s2k.php)) | Disputed: described on forums as the S950 OS adapted for the S900 | Yes | No | Floppy-loaded OS. Its origin is not documented. |
| MPC1000, MPC2500 | [JJOS Free](http://www7a.biglobe.ne.jp/~mpc1000/) | JJ | Yes (paid versions also exist) | No | Replacement OS. |
| MPC Live, X, One, Force (first generation) | [MPC-LiveXplore](https://github.com/TheKikGen/MPC-LiveXplore) and [MPCLiveXplore-libs](https://github.com/TheKikGen/MPCLiveXplore-libs) | TheKikGen | Yes | Yes | Root access, bootstrap and add-ons on the Linux-based units. Related community work includes Hakai OS and a modded Force firmware. |
| MPC Sample, MPC Sample Key | Opened by Akai | inMusic | Yes | Partly; scope not yet clear | Akai announced on 28 October 2026 that these units are open to custom firmware. inMusic's GitHub release covers the Linux components its licences require, not the MPC OS. |

No free firmware mod was found for the MPC60, ASQ10, MPC4000, MPC500,
MPC5000, S1000, S1100, S2000, S3000 family, S5000, S6000, Z4 or Z8. The
MPC60's version 3.10 is a paid EPROM set from Roger Linn Design. Late
official OS versions (for example S3000XL OS 2.0) are Akai's own and are
not mods.

## What to do with this list

If you use a source here to establish something about a machine, record
it in that machine's folder as a finding or a `machine.toml` fact with
`status = "documented"` and the source named precisely. If you find a
source that is missing, add it to this file.
