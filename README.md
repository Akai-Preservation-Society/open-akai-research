# Open Akai Research

A shared, open record of how vintage Akai samplers and MPCs work inside:
memory maps, boot paths, firmware structure, hardware registers, file
formats, and tools for building on them.

The aim is simple. Document what has been discovered, so the next person
starts where the last one stopped and not from zero.

It is written to be read by people and by AI coding agents. Clone it,
point your agent at it, and describe what you want your machine to do.
The agent can see what is established, what is a guess, and what nobody
knows yet.

## What is here today

See [STATUS.md](STATUS.md) for the current table and [GAPS.md](GAPS.md)
for what is missing. In brief:

| Machine | State |
|---|---|
| [Akai MPC3000](machines/mpc3000/README.md) | Hardware, addressing, boot path, BIOS services, a tested route for running your own program from floppy, and a map of OS 3.16 with a tested method for extending it. Sequencer, sampling and MIDI internals are mostly undocumented. |
| [Akai MPC2000XL](machines/mpc2000xl/README.md) | OS 1.20 image and flash update, recovery, addressing, panel and LED protocols, MIDI output, calling conventions, SND/PGM layouts, and a tested route for patching and flashing the OS. Sample engine and sequencer are undocumented. |
| [Akai MPC2000](machines/mpc2000/README.md) | OS 1.72 identified by hash; address model, OS services, in-RAM program and sequence layouts and disk services, from a published mod source checked against the bytes. Hardware and boot path undocumented; nothing hardware-tested. |
| [Akai MPC60](machines/mpc60/README.md) | Hardware, memory and I/O maps and ROM hashes from MAME's driver source (documented, unverified). No OS research yet. |
| [Akai S950](machines/s950/README.md) | Hardware, memory and I/O maps and ROM hashes from MAME's driver source (documented, unverified). No OS research yet. |
| [Akai S3200](machines/s3200/README.md) | The OS 2.00 EPROM pair labelled for the S3000 and S3200 (MAME's `s3000` set): image layout, reset and RAM relocation, segments, memory use, OS load and save from floppy and hard disk, disk layouts and peripheral set-up, mostly `static`. Not hardware-tested. Whether an S3200 runs this image or an XL-board OS is open. |
| [Akai S900](machines/s900/README.md) | Hardware, memory and I/O maps and ROM hashes from MAME's driver source (documented, unverified). No OS research yet. |

For manuals, emulators, tools and free mods that live elsewhere, see
[docs/external-resources.md](docs/external-resources.md).

## What is deliberately not here

- **No firmware.** No ROM dumps, EPROM images, OS disks or update files, from Akai or from anyone else. Images are identified by hash so you can check your own.
- **No disassembly listings** of manufacturers' or other developers' code. Findings describe behaviour and give addresses.
- **No manuals or schematics.** They are cited, not copied.
- **Nothing about defeating copy protection or licensing** in any firmware.
- **No guarantee.** Much of this has only been checked in an emulator. Every claim says how it was established. You change a rare instrument at your own risk; read [docs/safety.md](docs/safety.md).

See [LEGAL.md](LEGAL.md) for the reasoning.

## Use it with an AI agent

```sh
git clone https://github.com/Akai-Preservation-Society/open-akai-research
cd open-akai-research
```

Open the folder in your agent (Claude Code, Codex, Cursor or another).
It will read [AGENTS.md](AGENTS.md), which tells it how to use the
repository and where its limits are. Then say what you want, for example:

> I have an MPC3000 with OS 3.12. I want it to show a custom message at
> start-up from a floppy. What is possible, and what would you need to
> find out first?

A good answer starts by identifying your exact firmware and telling you
which parts are established and which are not.

## Use it yourself

Python 3.11 or newer, no packages to install.

```sh
python3 tools/oar.py find floppy --machine mpc3000    # search
python3 tools/oar.py symbol loader                    # named addresses
python3 tools/oar.py identify LS.bin MS.bin           # which firmware do I have?
python3 tools/oar.py verify mpc3000-v3.12 linear.bin  # does my image match the record?
python3 tools/oar.py check                            # validate the repository
```

Try the MPC3000 floppy route:

```sh
python3 machines/mpc3000/tools/sysdisk.py hello --text "HELLO FROM RAM" \
    -o build/HELLO.SYS --disk build/hello.img
```

## How the knowledge is organised

Every statement carries one of six evidence classes, from `hardware`
(seen on a real machine) down to `open` (unknown). They are defined in
[docs/evidence.md](docs/evidence.md). Addresses are tied to a specific
firmware image, and byte ranges that findings rely on are pinned by hash
so anyone holding that image can confirm them without the repository
containing a byte of it. Formats are in
[docs/data-formats.md](docs/data-formats.md).

## Contribute

One confirmed address is a useful contribution. So is a correction, a
hardware test of something only tried in an emulator, or a well-posed
question. You keep ownership of your own projects and decide what to
share; nobody is asked to open-source finished firmware. See
[CONTRIBUTING.md](CONTRIBUTING.md).

Work on a machine that is not listed is welcome: copy
[templates/machine.toml](templates/machine.toml) into a new folder under
`machines/`.

## Licence

Documentation and data: [Creative Commons Attribution 4.0](LICENSE).
Code in `tools/`, `tests/` and `machines/*/tools/`: [MIT](LICENSE-CODE).

This project is independent. It is not affiliated with, endorsed by or
sponsored by Akai Professional, inMusic Brands, Roger Linn Design or any
other company or developer named in it. Product names are used only to
identify the instruments described.
