# What this project publishes, and what it does not

This is a statement of the project's rules and the reasons for them. It
is not legal advice; laws differ between countries, and anyone with a
specific concern should ask a lawyer.

## The line

**Published here:** facts about how machines work. Chip identities,
memory maps, addresses of routines, descriptions of what code does,
data structures, file formats, hashes that identify images, original
tools, and original example code.

**Never published here:**

1. **Firmware.** No ROM or EPROM dumps, OS disks, update files or patched
   copies of them, in whole or in substantial part, whoever wrote them.
   This covers manufacturers' firmware and operating systems written by
   independent developers alike.
2. **Disassembly or decompilation listings** of other people's code. A
   finding may quote a few instructions where that is the clearest way
   to identify a place, and may describe a routine in pseudo-code. It
   may not reproduce a routine.
3. **Manuals, schematics and datasheets.** Cite them: title, edition,
   page.
4. **Anything whose purpose is to defeat copy protection, licensing,
   registration or personalisation** in any firmware, or to make a copy
   of a paid product work on a machine it was not sold for. This is out
   of scope even as a "fact".
5. **Other people's unpublished work** without their agreement.

The checker refuses common image file types, and `.gitignore` excludes
them, as a safety net. The responsibility stays with the contributor.

## How to work within the line

- **Identify images by hash.** `firmware.toml` holds hashes and says how
  an image can be obtained lawfully, which for EPROM machines normally
  means reading the chips of a machine you own.
- **Pin, do not paste.** To show that a claim concerns particular bytes,
  record the SHA-256 of the byte range (`oar.py pin`).
- **Share changes as patch manifests.** A manifest has offsets and new
  bytes only (`oar.py patch-diff`). The recipient applies it to their
  own image.
- **Share builders, not built files,** when a built file would contain
  firmware. A script that reads the user's own dump is fine; its output
  is not for distribution.

## Independent developers' operating systems

Several machines have operating systems written by members of the
community, some sold commercially and some given away. They are
documented here on the same terms as manufacturers' firmware, with one
addition: be considerate. Those developers are the people this project
hopes will join it. If you are the author of firmware described here
and want something corrected or reconsidered, open an issue or contact
the maintainers.

## Your contribution

By opening a pull request you state that:

- the contribution is your own work, or you have the right to submit it;
- it contains none of the material excluded above;
- you license documentation and data under CC BY 4.0 and code under the
  MIT licence, the licences of this repository.

Keep ownership of your own projects. Nothing here asks anyone to publish
finished firmware.

## Names

Akai, MPC and other product and company names belong to their owners.
They are used here only to identify the instruments being described.
This project is not affiliated with or endorsed by any of them.

## Concerns and removal requests

If you believe something here should not be published, open an issue or
contact the maintainers. Material that crosses the line above will be
removed.
