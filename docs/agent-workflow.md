# From a feature request to a tested change

A procedure for AI agents (and people) helping someone modify a machine.
Do the steps in order. Most disappointments come from skipping step 3.

## 1. Find out what the user has

Ask for, or work out:

- the machine model;
- the operating-system version it shows at start-up;
- whether they have a dump of its firmware as files, and if not, whether they can make one;
- how they can get code onto the machine (floppy drive, floppy emulator, EPROM programmer, SCSI);
- whether an emulator is available to them.

## 2. Identify the firmware by its bytes

```sh
python3 tools/oar.py identify <file> [<second chip file>]
python3 tools/oar.py verify <firmware-id> <linear image>
```

- If `identify` finds a match and `verify` passes, every finding listing that firmware id applies.
- If there is no match, the image is unknown. Findings marked `firmware: ["hardware"]` still apply. Findings keyed to other images do **not**, until you check each byte range you intend to rely on. Record the new image in `firmware.toml` (hashes only).
- If the user has no dump, only firmware-independent findings and routes that do not depend on fixed addresses are safe.

## 3. Decide whether the request is feasible, and say so

Break the feature into what it needs: which hardware it touches (display,
pads, audio, disk, MIDI), which OS behaviour it changes, where new code
would live, and how it would be delivered.

For each need, search:

```sh
python3 tools/oar.py find <words> --machine <id>
python3 tools/oar.py symbol <words> --firmware <firmware-id>
```

and read the machine's README and [GAPS.md](../GAPS.md). Put each need in
one of three columns:

| Established | Hypothesis only | Missing |
|---|---|---|
| A finding with a claim tagged `hardware`, `emulator`, `static` or `documented` covers it, for this firmware | Covered only by `hypothesis` claims | No finding, or an open question |

Then tell the user which situation they are in, before writing any code:

- **Buildable now.** Everything is in the first column.
- **Buildable after research.** Name the research: the open questions that block it, what answering them takes, and whether you can do it together now (for example, by analysing their image).
- **Not known to be possible.** The area is undocumented. Say so plainly. Offer to start the research and record it.

Do not fill a gap with what a similar machine does, with what an 8086 PC
would do, or with a plausible-looking address.

## 4. Choose how the change is delivered

Prefer, in this order:

1. **Loaded into RAM from removable media.** Nothing on the machine changes; removing the disk undoes it.
2. **A change to a file the machine loads** (for example a floppy-loaded OS file).
3. **Reprogrammed EPROMs or flash.** Last, and only with a verified backup of the originals. See [safety.md](safety.md).

The machine's README says which routes exist and how far each has been tested.

## 5. Design against recorded facts

- Take hook points and service entry points from the symbol table for the user's firmware id, not from memory.
- Follow the machine's calling convention finding for any OS routine you call or replace.
- Keep replaced instructions the same length, or pad. Check every other user of anything you change.
- Check where your code and data will live against the memory findings.
- Anything you derive yourself from the user's image is new research. Keep notes; you will record it in step 8.

## 6. Build

- Write outputs to `build/`. Never write into the user's original image files.
- Describe a change to an existing image as a patch manifest (`oar.py patch-diff`), which contains offsets and new bytes only.
- Use the machine's own tools in `machines/<id>/tools/` where they exist; they enforce rules that were learned the hard way.

## 7. Test, weakest environment first

1. **Static checks.** The tools' own checks; re-read your patch against the image.
2. **Emulator**, if one runs this machine. Make the change prove itself: a boot that looks normal may be the original firmware running. Show something only your change can show.
3. **Hardware**, with the user. Give them a short checklist: what to do, what they should see, what to do if they see something else, and how to get back to a working machine. One change at a time.

Report honestly which of these were done.

## 8. Record what was learned

Whatever happened, the repository should know more afterwards:

- a new finding, or a stronger tag on an existing one (an emulator result confirmed on hardware is a real contribution);
- a correction, if something recorded here was wrong;
- an open question for whatever stopped you;
- new symbols and pins.

Run `python3 tools/oar.py build` and `python3 tools/oar.py check`, and
offer the user a pull request.
