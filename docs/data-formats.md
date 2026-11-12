# Data formats

Everything is plain text: Markdown, TOML and CSV. `python3 tools/oar.py
check` enforces what is written here, and `index.json` is generated from
it. If you change a format, change the checker and this file together.

## Machine folder

```
machines/<machine>/
    README.md
    machine.toml
    firmware.toml
    hardware/*.csv
    findings/*.md
    questions/*.md
    symbols/<firmware-id>.csv
    pins/<firmware-id>.csv
    tools/
```

`<machine>` is a short lower-case id such as `mpc3000` or `s950`.

## `machine.toml`

```toml
id = "mpc3000"                 # equals the folder name
name = "Akai MPC3000"
coverage = "partial"           # none | seed | partial | substantial
summary = "One or two sentences on what is and is not documented."

[[fact]]
key = "main_cpu"               # unique within the file
value = "NEC uPD70236 (V53)"
status = "documented"          # an evidence class
source = "Where this came from, precisely"
```

Facts are for things that fit on a line. Anything that needs explaining
is a finding.

## `firmware.toml`

Identifies images. It never contains them.

```toml
[[image]]
id = "mpc3000-v3.12"           # starts with the machine id and a hyphen
label = "OS 3.12 (EPROM pair)"
origin = "manufacturer"        # manufacturer | community
kind = "eprom-pair"            # free text: eprom-pair, eprom, floppy-sys, flash ...
obtain = "How someone gets this image lawfully, e.g. by reading their own chips."
notes = "Optional."
size = 524288                  # of the whole (linear) image
sha256 = "..."                 # of the whole (linear) image
source = "Where the hashes came from."

[[image.part]]                 # optional: one per physical chip or file
role = "ls-even"
size = 262144
crc32 = "d4fb6439"
sha1 = "..."
sha256 = "..."
```

Hashes are lower-case hex. Give as many of `sha256`, `sha1` and `crc32`
as you have; `sha256` is preferred.

The **linear image** of a machine is defined in that machine's
`findings/address-model.md` or `eprom-layout.md` (for an even/odd EPROM
pair it is the two files interleaved). File offsets everywhere in the
machine's folder refer to the linear image.

## Findings: `findings/<name>.md`

Front matter is a flat list of `key: value` lines between two `---`
lines. A value is a plain string, a double-quoted string (required if it
contains `: `), or a JSON array of strings. This is valid YAML and needs
no YAML library to read.

```
---
id: mpc3000.floppy-sys-loader          # <machine>.<file name without .md>
title: The ROM floppy loader that runs a .SYS file at power-on
machine: mpc3000
area: boot
firmware: ["mpc3000-v3.11", "mpc3000-v3.12"]   # ids from firmware.toml, or ["hardware"]
status: emulator                       # class of the main result; never "open"
hardware_tested: partial               # yes | partial | no
summary: One sentence, at most 300 characters, that an agent can act on.
contributors: ["handle"]
last_verified: 2026-09-25              # when the evidence was last produced or re-checked
sources: ["Document or source file"]   # optional
depends_on: ["mpc3000.address-model"]  # optional: findings to read first
---
```

`area` is one of: `hardware`, `cpu`, `memory`, `boot`, `firmware`, `os`,
`display`, `panel`, `storage`, `audio`, `midi`, `sequencer`,
`file-format`, `modding`, `tooling`.

Use `firmware: ["hardware"]` for facts that do not depend on the
firmware.

The body must contain these three headings:

- `## Claims`: a list. **Every top-level bullet starts with a tag**:
  `- **[static]** The routine at ...`. Tags are the six evidence classes.
  At least one claim must carry the finding's `status`. Sub-headings
  (`###`) and tables between bullets are fine.
- `## Evidence`: how each class of claim was established, in enough
  detail to repeat.
- `## Open questions`: links to files in `questions/`, or "None known."

Other headings are allowed. A recipe is a finding with `area: modding`
and a `## Steps` section.

## Questions: `questions/<name>.md`

```
---
id: mpc3000.q.panel-protocol           # <machine>.q.<file name>
title: Front-panel protocol
machine: mpc3000
area: panel
status: open                           # always
priority: high                         # high | medium | low
needs: ["firmware-image", "analysis"]  # hardware | emulator | firmware-image | document | analysis
summary: One sentence.
blocks: ["mpc3000.build-a-floppy-sys"] # optional: what cannot progress without it
related: ["mpc3000.memory-and-io-map"] # optional
---
```

Required headings: `## What is unknown`, `## Why it matters`,
`## How to answer it`.

When a question is answered, delete it and add or extend a finding in
the same pull request.

## Symbols: `symbols/<firmware-id>.csv`

Named addresses for one firmware image.

```
name,kind,address,file_offset,size,status,finding,notes
startup_loader,code,B000:01A7,0x301A7,525,static,mpc3000.floppy-sys-loader,Startup-file loader
```

- `name`: `lower_snake_case`, unique in the file. Use the same name for the same thing across images.
- `kind`: `code`, `data`, `string`, `table`, `vector`, `io`, `ram`, `range`.
- `address`: in the form the code uses on that machine (may be empty for a range).
- `file_offset`: linear file offset as `0x...` (may be empty for RAM and I/O).
- `size`: bytes, decimal; empty if unknown.
- `finding`: the id of the finding that establishes it. Every symbol has one.

## Pins: `pins/<firmware-id>.csv`

A pin is the SHA-256 of a byte range of an image. Pins let anyone with
the image confirm that a finding is talking about their bytes, and let
`oar.py verify` reject an image that differs, without the repository
holding any firmware.

```
file_offset,length,sha256,label,finding
0x78143,468,8edaf657...,INT 45h MZ loader,mpc3000.floppy-sys-loader
```

Make a row with:

```sh
python3 tools/oar.py pin <linear image> 0x78143 468 --label "INT 45h MZ loader" --finding mpc3000.floppy-sys-loader
```

Pin the bytes a claim depends on: the routine, the table, the string.
Do not pin whole images here; that is what `firmware.toml` is for.

## Hardware tables: `hardware/*.csv`

Any columns you need, plus two that are required: `status` and `source`.
Existing tables: `memory-map.csv`, `io-ports.csv`, `interrupts.csv`.

## Patch manifests

A way to share a change to an image without sharing the image. Made by
`oar.py patch-diff`, applied by `oar.py patch-apply`.

```toml
format = "oar-patch-1"
name = "example"
firmware = "mpc3000-v3.12"
description = "What it does."
base_sha256 = "..."            # the image it applies to
result_sha256 = "..."          # the image it produces

[[hunk]]
offset = 0x30207               # linear file offset
length = 1
old_sha256 = "..."             # hash of the bytes being replaced, not the bytes
new = "EB"                     # the new bytes, hex
why = "One line on what this hunk changes."
```

A manifest holds only new bytes. `patch-apply` refuses to run if the
base image or any replaced range is not what the manifest expects.

## Generated files

`index.json`, `STATUS.md` and `GAPS.md` are written by
`python3 tools/oar.py build`. Do not edit them. `check` fails if they are
out of date.
