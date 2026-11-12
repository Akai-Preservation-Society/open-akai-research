# Contributing

Thank you. One confirmed fact is a contribution. You do not need to be a
maintainer, to share a whole project, or to write well.

## What helps most

1. **Hardware confirmation** of something marked `emulator` or `static`. See the lists in [GAPS.md](GAPS.md).
2. **Answers to open questions.** High-priority ones are at the top of each machine's list.
3. **A first finding for a machine that has none.**
4. **Corrections.** If something here is wrong, say so; a retraction with a reason is as valuable as a discovery.
5. **New questions,** well posed: what is unknown, why it matters, how it could be answered.
6. **Tools** that others can reuse.

## Ways to contribute

- **An issue.** Use the "Finding", "Correction" or "Open question" form. A maintainer or another contributor can turn it into files.
- **A pull request.** Add or edit files directly.
- **With an AI agent.** Clone the repository, let the agent read [AGENTS.md](AGENTS.md), do your work, and ask it to record what was learned and prepare the pull request. Check what it wrote: you are responsible for the evidence tags.

## Adding a finding

1. Copy [templates/finding.md](templates/finding.md) to `machines/<machine>/findings/<short-name>.md`.
2. Fill in the front matter. Name the exact firmware ids it applies to; add new images to `firmware.toml` by hash.
3. Write each claim as one bullet starting with its evidence tag. Use the weakest tag that is honest. Classes are defined in [docs/evidence.md](docs/evidence.md).
4. Say in **Evidence** how someone else can repeat it.
5. Add named addresses to `symbols/<firmware-id>.csv` and pin the bytes they rely on (`python3 tools/oar.py pin`).
6. Link the open questions that remain, and write new ones.
7. Run:

   ```sh
   python3 tools/oar.py build
   python3 tools/oar.py check
   python3 -m unittest discover -s tests
   ```

Formats are in [docs/data-formats.md](docs/data-formats.md).

## Rules

- **Nothing excluded by [LEGAL.md](LEGAL.md):** no firmware, no listings, no manuals, nothing aimed at defeating protection or licensing.
- **Tag honestly.** An emulator run is not a hardware test. A guess is a `hypothesis` however confident you are.
- **Addresses name their firmware image.** A finding without a firmware id cannot be used safely.
- **Credit the source.** Put your handle in `contributors`, and name earlier work you built on in `sources`, including other people's projects, forum posts and emulator source files. If you know who first found something, say so.
- **Write plainly.** Short sentences, exact numbers, hex with `0x` or a trailing `h` as the machine's findings do. Many readers use English as a second language, and many readers are programs.
- **One topic per finding.** Split rather than grow.
- **Do not edit generated files** (`index.json`, `STATUS.md`, `GAPS.md`).

## Adding a machine

Create `machines/<id>/`, copy [templates/machine.toml](templates/machine.toml)
into it as `machine.toml`, add a short `README.md`, and add at least one
question saying what should be found out first. Add `firmware.toml` once
an image can be identified by hash.

## Review

Maintainers check that the format is valid, that the evidence supports
the tags, and that nothing excluded has been included. They do not need
to be able to reproduce a hardware result to accept it, but they may ask
how it was obtained. Disagreements about a fact are settled by evidence;
until then both readings are recorded, tagged `hypothesis`.

## Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). In one line: be kind, be
exact, give credit.

## Licence

Documentation and data are licensed under CC BY 4.0 and code under MIT.
By contributing you agree to license your contribution the same way and
confirm the statements in [LEGAL.md](LEGAL.md).
