# Evidence classes

Reverse engineering produces statements of very different strength. A
wrong address can cost someone days, or a machine. So every statement in
this repository says how it was established, using one of six classes.

| Class | Meaning | Typical wording in a claim |
|---|---|---|
| `hardware` | Observed on a physical machine. | "appears on the LCD of a real unit" |
| `emulator` | Observed in an emulator run. | "in MAME, reaches the Play/Record screen" |
| `static` | Read from the firmware bytes by analysis someone else can repeat. | "the routine at X writes port Y" |
| `documented` | Taken from a primary document or from emulator source code, and not independently checked here. | "the service manual lists" |
| `hypothesis` | A reasoned guess with its reasons given. Not tested. | "this bit is probably the ready flag" |
| `open` | Unknown. | "nobody has determined" |

`hardware`, `emulator`, `static` and `documented` are **established**:
you may build on them, within what each one proves. `hypothesis` and
`open` are not.

## What each class does and does not prove

**`hardware`** proves that the thing happened on that unit, with that
firmware, on that day. Say which firmware and how many runs. It does not
prove it for other firmware versions or board revisions.

**`emulator`** proves what a model of the hardware did. Emulator drivers
for these machines are incomplete, and some are marked as not working by
their own authors. A trace is one execution: it shows that a path runs,
not that no other path exists.

**`static`** proves what the code says, on every path that was actually
decoded. It does not prove how a chip responds to what the code sends
it. A `static` claim must be repeatable: give the firmware id, the linear
file offset, and what to look at. Where possible, pin the bytes
(see [data-formats.md](data-formats.md)).

**`documented`** is only as good as the document. Manuals contain
errors and emulator sources contain guesses, which their authors often
mark as such. Name the document precisely.

**`hypothesis`** is welcome. A stated guess with reasons is far more
useful than silence, provided nobody mistakes it for a fact. Say what
would confirm or refute it.

## How the classes appear

- **Findings** have a `status`: the class of the finding's main result,
  the sentence in its `summary`.
- **Claims** inside a finding each start with their own tag, for example
  `- **[static]** ...`. A finding with status `static` may well contain
  `hypothesis` and `open` claims; that is normal and useful.
- **`hardware_tested`** on a finding says whether any of it has been
  checked on a real machine: `yes` (its main result), `partial` (some
  claims), or `no`.
- **Facts** in `machine.toml`, rows in `hardware/*.csv` and rows in
  `symbols/*.csv` each carry a `status`.
- **Questions** are always `open`.

## Raising and lowering a class

Evidence can be upgraded: a contributor who runs an emulator-only result
on a real machine changes the tag to `hardware`, adds what they did to
the Evidence section, and updates `last_verified`.

It can also be downgraded. If you cannot reproduce a claim, say so in an
issue or a pull request and lower the tag. A retraction is a
contribution. Keep a line in the Evidence section recording what was
believed before and why it was wrong, so the mistake is not repeated.

## Minimum evidence to record

| Class | Record at least |
|---|---|
| `hardware` | Date, firmware id (verified by hash where possible), what was done, what was seen, how many times; a photo or capture if you have one |
| `emulator` | Emulator name and version or commit, firmware id, inputs, what was observed |
| `static` | Firmware id, linear file offsets, the method, and a pin where bytes matter |
| `documented` | Document title, edition or date, page or section; for source code, the file path |
| `hypothesis` | The reasons, and the test that would settle it |
