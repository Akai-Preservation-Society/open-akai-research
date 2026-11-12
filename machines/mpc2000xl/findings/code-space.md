---
id: mpc2000xl.code-space
title: Where added code can and cannot go in OS 1.20
machine: mpc2000xl
area: modding
firmware: ["mpc2000xl-os1.20"]
status: hardware
hardware_tested: partial
summary: OS 1.20 has no documented free space. Ranges that must never be written are listed with the reason. Room has been made by retiring features whose code is proven never to run; zero bytes alone do not make a range safe.
contributors: ["open-akai-research"]
last_verified: 2026-10-07
depends_on: ["mpc2000xl.address-model", "mpc2000xl.rom-and-flash"]
---

# Where added code can and cannot go in OS 1.20

## Claims

- **[hardware]** A range of zero bytes in the image is not free space. The 1,149 zero bytes at file `0x10036-0x104B3` held code that worked warm and then froze or crashed after a cold boot.
- **[static]** Never write these ranges ([../tools/xlimage.py](../tools/xlimage.py) `compare` refuses them):

  | File range | Why |
  |---|---|
  | `0x10036-0x104B3` | Cold-boot freeze and crash on hardware; mapping at cold boot unknown |
  | `0x25BDD-0x25BED` | Scratch buffer for the `.ALL` loader's header |
  | `0x74000-0x747FF` | Zero in the image but RAM at run time: the end of the 24-record Program pool starts here |
  | `0x77FFE-0x77FFF` | The checksum word |
  | `0x78000-0x7BFFF` | Erased by an update and never programmed |
  | `0x7C000-0x7FFFF` | Boot and recovery block; an update never writes it |

- **[static]** File `0x75C00-0x76800` has been proposed as a code bank but is not proven unused.
- **[hardware]** The proven way to make room is to retire a feature: disable its entry points, show by an execution watch that its code is never run or read, then reuse it.
- **[hardware]** Code placed in the RAM copy of segment `7400` (file `0x74800` onward, outside the ranges above) runs on hardware when it is entered through a gate that checks the module's header ([address-model.md](address-model.md)).
- **[hypothesis]** That RAM copy stays writable and mapped the same way on every unit.
- **[open]** A census of every range that OS 1.20 never executes or reads.

## Evidence

- **Static:** the reserved ranges from the update's write range, the `.ALL` loader (`0x1DA43`) and the Program-pool bounds.
- **Hardware:** PGR5-gap freezes in July 2026; space reclaimed by retiring a feature, and gated `7400` code, in every 2KXL PLUS image from v1.1 (September 2026) on.

## Open questions

- [The PGR5 gap at cold boot](../questions/pgr5-gap.md)
- [A map of the OS 1.20 code](../questions/os120-code-map.md)
