#!/usr/bin/env python3
"""oar - the Open Akai Research toolkit.

Python 3.11 or newer, standard library only. Run from anywhere:

    python3 tools/oar.py <command> --help

Commands
    check        validate every file in the knowledge base
    build        regenerate index.json, STATUS.md and GAPS.md
    find         search findings and open questions
    symbol       look up a named address
    identify     tell which known firmware image a file (or chip pair) is
    interleave   join an even/odd EPROM pair into one linear image
    split        split a linear image back into an even/odd EPROM pair
    pin          print a pins.csv row for a byte range of an image
    verify       check an image against the registry hash and every pin
    patch-diff   describe the difference between two images as a patch manifest
    patch-apply  apply a patch manifest to an image

The repository never contains firmware. Commands that read an image read
a file you supply.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import tomllib
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MACHINES = ROOT / "machines"

# Evidence classes, strongest first. See docs/evidence.md.
STATUSES = ["hardware", "emulator", "static", "documented", "hypothesis", "open"]
ESTABLISHED = {"hardware", "emulator", "static", "documented"}
RANK = {s: len(STATUSES) - i for i, s in enumerate(STATUSES)}

AREAS = [
    "hardware", "cpu", "memory", "boot", "firmware", "os", "display", "panel",
    "storage", "audio", "midi", "sequencer", "file-format", "modding", "tooling",
]
COVERAGE = ["none", "seed", "partial", "substantial"]
PRIORITIES = ["high", "medium", "low"]
NEEDS = ["hardware", "emulator", "firmware-image", "document", "analysis"]
SYMBOL_KINDS = ["code", "data", "string", "table", "vector", "io", "ram", "range"]
HARDWARE_TESTED = ["yes", "partial", "no"]

FINDING_KEYS = ["id", "title", "machine", "area", "firmware", "status",
                "hardware_tested", "summary", "contributors", "last_verified"]
FINDING_OPTIONAL = ["depends_on", "sources"]
FINDING_SECTIONS = ["## Claims", "## Evidence", "## Open questions"]
QUESTION_KEYS = ["id", "title", "machine", "area", "status", "priority", "needs", "summary"]
QUESTION_OPTIONAL = ["blocks", "related"]
QUESTION_SECTIONS = ["## What is unknown", "## Why it matters", "## How to answer it"]

SYMBOL_HEADER = ["name", "kind", "address", "file_offset", "size", "status", "finding", "notes"]
PIN_HEADER = ["file_offset", "length", "sha256", "label", "finding"]

GENERATED = {"index.json", "STATUS.md", "GAPS.md"}
CLAIM_RE = re.compile(r"^- \*\*\[([a-z]+)\]\*\* \S")
ID_RE = re.compile(r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HEX_RE = re.compile(r"^0x[0-9A-Fa-f]+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class Problems:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, path: Path | str, message: str) -> None:
        where = path.relative_to(ROOT) if isinstance(path, Path) and path.is_absolute() else path
        self.items.append(f"{where}: {message}")


# --- front matter -------------------------------------------------------------

def parse_front_matter(text: str) -> tuple[dict, str]:
    """Flat `key: value` front matter between two `---` lines.

    Values are plain strings, double-quoted strings, or JSON arrays of
    strings. Nothing else is accepted, so the block is valid YAML and can
    be read without a YAML library.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise ValueError("file does not start with a '---' front matter line")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        raise ValueError("front matter is not closed by a '---' line") from None
    meta: dict = {}
    for number, line in enumerate(lines[1:end], start=2):
        if not line.strip():
            continue
        match = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if not match:
            raise ValueError(f"line {number}: expected 'key: value', got {line!r}")
        key, raw = match[1], match[2].strip()
        if key in meta:
            raise ValueError(f"line {number}: duplicate key {key!r}")
        if raw.startswith("["):
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {number}: {key} is not a JSON array: {exc}") from None
            if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
                raise ValueError(f"line {number}: {key} must be an array of strings")
        elif raw.startswith('"'):
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {number}: {key} is not a quoted string: {exc}") from None
        else:
            if ": " in raw or raw.endswith(":") or raw[:1] in "{}&*!|>'%@`#":
                raise ValueError(f"line {number}: quote the value of {key} (it is not plain YAML)")
            value = raw
        meta[key] = value
    return meta, "\n".join(lines[end + 1:])


def sections(body: str) -> dict[str, str]:
    """Text under each `## ` heading."""
    out: dict[str, str] = {}
    current = None
    for line in body.split("\n"):
        if line.startswith("## "):
            current = line.strip()
            out[current] = ""
        elif current is not None:
            out[current] += line + "\n"
    return out


# --- loading ------------------------------------------------------------------

def machine_dirs() -> list[Path]:
    if not MACHINES.is_dir():
        return []
    return sorted(p for p in MACHINES.iterdir() if p.is_dir())


def load_toml(path: Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return list(reader.fieldnames or []), rows


def load_all(problems: Problems) -> dict:
    """Read the whole knowledge base into one structure, recording problems."""
    data = {"machines": {}}
    for mdir in machine_dirs():
        mid = mdir.name
        entry = {"id": mid, "dir": mdir, "meta": {}, "facts": [], "images": [],
                 "findings": [], "questions": [], "symbols": {}, "pins": {}, "tables": {}}
        data["machines"][mid] = entry

        mfile = mdir / "machine.toml"
        if not mfile.is_file():
            problems.add(mdir, "missing machine.toml")
        else:
            try:
                meta = load_toml(mfile)
            except tomllib.TOMLDecodeError as exc:
                problems.add(mfile, f"invalid TOML: {exc}")
                meta = {}
            entry["meta"] = {k: v for k, v in meta.items() if k != "fact"}
            entry["facts"] = meta.get("fact", [])
            check_machine(mfile, mid, meta, problems)

        ffile = mdir / "firmware.toml"
        if ffile.is_file():
            try:
                entry["images"] = load_toml(ffile).get("image", [])
            except tomllib.TOMLDecodeError as exc:
                problems.add(ffile, f"invalid TOML: {exc}")
            check_firmware(ffile, mid, entry["images"], problems)

        for kind, folder in (("findings", "findings"), ("questions", "questions")):
            fdir = mdir / folder
            if not fdir.is_dir():
                continue
            for path in sorted(fdir.glob("*.md")):
                try:
                    meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
                except (ValueError, UnicodeDecodeError) as exc:
                    problems.add(path, str(exc))
                    continue
                entry[kind].append({"path": path, "meta": meta, "body": body})

        for name, folder, header in (("symbols", "symbols", SYMBOL_HEADER), ("pins", "pins", PIN_HEADER)):
            fdir = mdir / folder
            if not fdir.is_dir():
                continue
            for path in sorted(fdir.glob("*.csv")):
                fields, rows = read_csv(path)
                if fields != header:
                    problems.add(path, f"header must be exactly {','.join(header)}")
                    continue
                entry[name][path.stem] = {"path": path, "rows": rows}

        hdir = mdir / "hardware"
        if hdir.is_dir():
            for path in sorted(hdir.glob("*.csv")):
                fields, rows = read_csv(path)
                entry["tables"][path.stem] = {"path": path, "fields": fields, "rows": rows}
    return data


# --- validation ---------------------------------------------------------------

def check_machine(path: Path, mid: str, meta: dict, problems: Problems) -> None:
    for key in ("id", "name", "coverage", "summary"):
        if not isinstance(meta.get(key), str) or not meta[key].strip():
            problems.add(path, f"missing string field {key!r}")
    if meta.get("id") != mid:
        problems.add(path, f"id {meta.get('id')!r} does not match the folder name {mid!r}")
    if meta.get("coverage") not in COVERAGE:
        problems.add(path, f"coverage must be one of {COVERAGE}")
    seen = set()
    for index, fact in enumerate(meta.get("fact", []), start=1):
        label = f"fact #{index} ({fact.get('key', '?')})"
        for key in ("key", "value", "status", "source"):
            if not isinstance(fact.get(key), str) or not fact[key].strip():
                problems.add(path, f"{label}: missing string field {key!r}")
        if fact.get("status") not in STATUSES:
            problems.add(path, f"{label}: status must be one of {STATUSES}")
        if fact.get("key") in seen:
            problems.add(path, f"{label}: duplicate key")
        seen.add(fact.get("key"))


def check_firmware(path: Path, mid: str, images: list, problems: Problems) -> None:
    seen = set()
    for image in images:
        iid = image.get("id", "?")
        label = f"image {iid}"
        for key in ("id", "label", "origin", "kind", "obtain"):
            if not isinstance(image.get(key), str) or not image[key].strip():
                problems.add(path, f"{label}: missing string field {key!r}")
        if not str(iid).startswith(mid + "-"):
            problems.add(path, f"{label}: id must start with '{mid}-'")
        if iid in seen:
            problems.add(path, f"{label}: duplicate id")
        seen.add(iid)
        if image.get("origin") not in ("manufacturer", "community"):
            problems.add(path, f"{label}: origin must be 'manufacturer' or 'community'")
        for holder, name in [(image, label)] + [(p, f"{label} part {p.get('role', '?')}") for p in image.get("part", [])]:
            for key, pattern in (("sha256", r"[0-9a-f]{64}"), ("sha1", r"[0-9a-f]{40}"), ("crc32", r"[0-9a-f]{8}")):
                if key in holder and not re.fullmatch(pattern, str(holder[key])):
                    problems.add(path, f"{name}: {key} is not lower-case hex of the right length")
            if "size" in holder and not isinstance(holder["size"], int):
                problems.add(path, f"{name}: size must be an integer")


def check_document(doc: dict, kind: str, mid: str, problems: Problems) -> None:
    path, meta, body = doc["path"], doc["meta"], doc["body"]
    required = FINDING_KEYS if kind == "finding" else QUESTION_KEYS
    optional = FINDING_OPTIONAL if kind == "finding" else QUESTION_OPTIONAL
    for key in required:
        if key not in meta or meta[key] in ("", []):
            problems.add(path, f"missing front matter key {key!r}")
    for key in meta:
        if key not in required and key not in optional:
            problems.add(path, f"unknown front matter key {key!r}")
    for key in ("firmware", "contributors", "depends_on", "sources", "needs", "blocks", "related"):
        if key in meta and not isinstance(meta[key], list):
            problems.add(path, f"{key} must be an array, e.g. [\"a\", \"b\"]")

    prefix = f"{mid}.q." if kind == "question" else f"{mid}."
    expected = prefix + path.stem
    if meta.get("id") != expected:
        problems.add(path, f"id must be {expected!r} (machine, then file name)")
    elif not ID_RE.match(meta["id"]):
        problems.add(path, "id may only use lower-case letters, digits, '.' and '-'")
    if meta.get("machine") != mid:
        problems.add(path, f"machine must be {mid!r}")
    if meta.get("area") not in AREAS:
        problems.add(path, f"area must be one of {AREAS}")
    if isinstance(meta.get("summary"), str) and len(meta["summary"]) > 300:
        problems.add(path, "summary is longer than 300 characters")

    parts = sections(body)
    wanted = FINDING_SECTIONS if kind == "finding" else QUESTION_SECTIONS
    for heading in wanted:
        if heading not in parts:
            problems.add(path, f"missing section {heading!r}")
        elif not parts[heading].strip():
            problems.add(path, f"section {heading!r} is empty")

    if kind == "question":
        if meta.get("status") != "open":
            problems.add(path, "a question's status is always 'open'")
        if meta.get("priority") not in PRIORITIES:
            problems.add(path, f"priority must be one of {PRIORITIES}")
        for need in meta.get("needs", []) if isinstance(meta.get("needs"), list) else []:
            if need not in NEEDS:
                problems.add(path, f"needs entry {need!r} is not one of {NEEDS}")
        return

    status = meta.get("status")
    if status not in STATUSES or status == "open":
        problems.add(path, "status must be hardware, emulator, static, documented or hypothesis "
                           "(an unknown belongs in questions/)")
    if meta.get("hardware_tested") not in HARDWARE_TESTED:
        problems.add(path, f"hardware_tested must be one of {HARDWARE_TESTED}")
    if not DATE_RE.match(str(meta.get("last_verified", ""))):
        problems.add(path, "last_verified must be a date, YYYY-MM-DD")

    tags = []
    for line in parts.get("## Claims", "").split("\n"):
        if not line.startswith("- "):
            continue
        match = CLAIM_RE.match(line)
        if not match:
            problems.add(path, f"claim does not start with a tag such as '- **[static]** ...': {line[:60]!r}")
            continue
        if match[1] not in STATUSES:
            problems.add(path, f"claim tag [{match[1]}] is not one of {STATUSES}")
        tags.append(match[1])
    doc["claim_tags"] = tags
    if parts.get("## Claims", "").strip() and not tags:
        problems.add(path, "the Claims section has no tagged bullet")
    if status in STATUSES and tags and status not in tags:
        problems.add(path, f"status is {status!r} but no claim carries that tag")
    if status == "hardware" and meta.get("hardware_tested") == "no":
        problems.add(path, "status is 'hardware' but hardware_tested is 'no'")
    if "hardware" in tags and meta.get("hardware_tested") == "no":
        problems.add(path, "a claim is tagged [hardware] but hardware_tested is 'no'")


def check_links(path: Path, body: str, problems: Problems) -> None:
    """Relative Markdown links must point at a file that exists."""
    for target in re.findall(r"\]\(([^)\s]+)\)", body):
        if re.match(r"^[a-z]+:", target) or target.startswith("#"):
            continue
        resolved = (path.parent / target.split("#")[0]).resolve()
        if resolved.parent == ROOT and resolved.name in GENERATED:
            continue  # written by `build`
        if not resolved.exists():
            problems.add(path, f"broken link: {target}")


def validate(data: dict, problems: Problems) -> None:
    finding_ids: dict[str, Path] = {}
    question_ids: dict[str, Path] = {}
    image_ids: set[str] = set()
    for mid, machine in data["machines"].items():
        image_ids.update(i.get("id") for i in machine["images"])
        for doc in machine["findings"]:
            check_document(doc, "finding", mid, problems)
            fid = doc["meta"].get("id")
            if fid in finding_ids:
                problems.add(doc["path"], f"id {fid!r} is already used by {finding_ids[fid].name}")
            finding_ids[fid] = doc["path"]
        for doc in machine["questions"]:
            check_document(doc, "question", mid, problems)
            question_ids[doc["meta"].get("id")] = doc["path"]

    known = set(finding_ids) | set(question_ids)
    for mid, machine in data["machines"].items():
        for doc in machine["findings"]:
            meta = doc["meta"]
            for fw in meta.get("firmware", []) if isinstance(meta.get("firmware"), list) else []:
                if fw != "hardware" and fw not in image_ids:
                    problems.add(doc["path"], f"firmware {fw!r} is not in any firmware.toml "
                                              "(use \"hardware\" for firmware-independent facts)")
            for ref in meta.get("depends_on", []) if isinstance(meta.get("depends_on"), list) else []:
                if ref not in finding_ids:
                    problems.add(doc["path"], f"depends_on names an unknown finding {ref!r}")
            check_links(doc["path"], doc["body"], problems)
        for doc in machine["questions"]:
            meta = doc["meta"]
            for key in ("blocks", "related"):
                for ref in meta.get(key, []) if isinstance(meta.get(key), list) else []:
                    if ref not in known:
                        problems.add(doc["path"], f"{key} names an unknown id {ref!r}")
            check_links(doc["path"], doc["body"], problems)

        for fw, table in machine["symbols"].items():
            if fw not in image_ids:
                problems.add(table["path"], f"file name {fw!r} is not a firmware id in firmware.toml")
            names = set()
            for number, row in enumerate(table["rows"], start=2):
                where = f"row {number} ({row['name']})"
                if not re.fullmatch(r"[a-z][a-z0-9_]*", row["name"]):
                    problems.add(table["path"], f"{where}: name must be lower_snake_case")
                if row["name"] in names:
                    problems.add(table["path"], f"{where}: duplicate name")
                names.add(row["name"])
                if row["kind"] not in SYMBOL_KINDS:
                    problems.add(table["path"], f"{where}: kind must be one of {SYMBOL_KINDS}")
                if row["status"] not in STATUSES:
                    problems.add(table["path"], f"{where}: status must be one of {STATUSES}")
                if row["file_offset"] and not HEX_RE.match(row["file_offset"]):
                    problems.add(table["path"], f"{where}: file_offset must look like 0x1A2B")
                if row["size"] and not row["size"].isdigit():
                    problems.add(table["path"], f"{where}: size must be a decimal byte count")
                if not row["address"] and not row["file_offset"]:
                    problems.add(table["path"], f"{where}: needs an address or a file_offset")
                if row["finding"] not in finding_ids:
                    problems.add(table["path"], f"{where}: finding {row['finding']!r} does not exist")

        for fw, table in machine["pins"].items():
            if fw not in image_ids:
                problems.add(table["path"], f"file name {fw!r} is not a firmware id in firmware.toml")
            for number, row in enumerate(table["rows"], start=2):
                where = f"row {number}"
                if not HEX_RE.match(row["file_offset"]):
                    problems.add(table["path"], f"{where}: file_offset must look like 0x1A2B")
                if not row["length"].isdigit() or int(row["length"]) < 1:
                    problems.add(table["path"], f"{where}: length must be a positive decimal byte count")
                if not SHA256_RE.match(row["sha256"]):
                    problems.add(table["path"], f"{where}: sha256 must be 64 lower-case hex digits")
                if not row["label"].strip():
                    problems.add(table["path"], f"{where}: label is empty")
                if row["finding"] not in finding_ids:
                    problems.add(table["path"], f"{where}: finding {row['finding']!r} does not exist")

        for name, table in machine["tables"].items():
            if "status" not in table["fields"] or "source" not in table["fields"]:
                problems.add(table["path"], "hardware tables need 'status' and 'source' columns")
                continue
            for number, row in enumerate(table["rows"], start=2):
                if row["status"] not in STATUSES:
                    problems.add(table["path"], f"row {number}: status must be one of {STATUSES}")
                if not row["source"].strip():
                    problems.add(table["path"], f"row {number}: source is empty")

    forbidden = {".bin", ".rom", ".eprom", ".sys", ".img", ".ima", ".iso", ".hfe", ".pdf"}
    for path in sorted(ROOT.rglob("*")):
        if ".git" in path.parts or "build" in path.relative_to(ROOT).parts or not path.is_file():
            continue
        if path.suffix.lower() in forbidden:
            problems.add(path, "firmware images, disk images and manuals are not stored here (see LEGAL.md)")
        elif path.stat().st_size > 1_000_000:
            problems.add(path, "file is larger than 1 MB; link to it instead")


# --- generated files ----------------------------------------------------------

def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def build_index(data: dict) -> dict:
    index = {"format": "oar-index-1", "statuses": STATUSES, "areas": AREAS, "machines": []}
    for mid, machine in data["machines"].items():
        index["machines"].append({
            "id": mid,
            **machine["meta"],
            "facts": machine["facts"],
            "firmware": [{k: v for k, v in image.items()} for image in machine["images"]],
            "findings": [{**doc["meta"], "path": rel(doc["path"])} for doc in machine["findings"]],
            "questions": [{**doc["meta"], "path": rel(doc["path"])} for doc in machine["questions"]],
            "symbols": {fw: {"path": rel(t["path"]), "count": len(t["rows"])}
                        for fw, t in machine["symbols"].items()},
            "pins": {fw: {"path": rel(t["path"]), "count": len(t["rows"])}
                     for fw, t in machine["pins"].items()},
            "hardware_tables": {n: {"path": rel(t["path"]), "rows": len(t["rows"])}
                                for n, t in machine["tables"].items()},
        })
    return index


def build_status(data: dict) -> str:
    out = ["# Status", "",
           "Generated by `python3 tools/oar.py build`. Do not edit by hand.", "",
           "How much is known about each machine, and how well it is established. "
           "Evidence classes are defined in [docs/evidence.md](docs/evidence.md).", "",
           "| Machine | Coverage | Facts | Findings | Hardware-tested findings | Symbols | Firmware images | Open questions |",
           "|---|---|---|---|---|---|---|---|"]
    for mid, m in data["machines"].items():
        tested = sum(1 for d in m["findings"] if d["meta"].get("hardware_tested") in ("yes", "partial"))
        symbols = sum(len(t["rows"]) for t in m["symbols"].values())
        out.append(f"| [{m['meta'].get('name', mid)}](machines/{mid}/README.md) | {m['meta'].get('coverage', '?')} "
                   f"| {len(m['facts'])} | {len(m['findings'])} | {tested} | {symbols} "
                   f"| {len(m['images'])} | {len(m['questions'])} |")
    out.append("")
    for mid, m in data["machines"].items():
        if not m["findings"]:
            continue
        out += [f"## {m['meta'].get('name', mid)}", "",
                "| Area | Finding | Evidence | Hardware tested | Firmware | Last verified |",
                "|---|---|---|---|---|---|"]
        for doc in sorted(m["findings"], key=lambda d: (AREAS.index(d["meta"].get("area")) if d["meta"].get("area") in AREAS else 99, d["meta"].get("id", ""))):
            meta = doc["meta"]
            firmware = ", ".join(f.removeprefix(mid + "-") for f in meta.get("firmware", []))
            out.append(f"| {meta.get('area')} | [{meta.get('title')}]({rel(doc['path'])}) | {meta.get('status')} "
                       f"| {meta.get('hardware_tested')} | {firmware} | {meta.get('last_verified')} |")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def build_gaps(data: dict) -> str:
    out = ["# Gaps", "",
           "Generated by `python3 tools/oar.py build`. Do not edit by hand.", "",
           "What this repository does not know. Read this before promising a user "
           "that something can be built. Anything not listed here and not covered "
           "by a finding is also unknown: absence of a finding is never evidence.", ""]
    empty = [m for m in data["machines"].values() if m["meta"].get("coverage") == "none"]
    if empty:
        out += ["## Machines with no research yet", ""]
        out += [f"- **{m['meta'].get('name', m['id'])}** (`machines/{m['id']}/`): {m['meta'].get('summary', '')}" for m in empty]
        out.append("")
    for mid, m in data["machines"].items():
        block = []
        if m["questions"]:
            block += ["### Open questions", "",
                      "| Priority | Area | Question | Needs |", "|---|---|---|---|"]
            for doc in sorted(m["questions"], key=lambda d: (PRIORITIES.index(d["meta"].get("priority")) if d["meta"].get("priority") in PRIORITIES else 9, d["meta"].get("id", ""))):
                meta = doc["meta"]
                block.append(f"| {meta.get('priority')} | {meta.get('area')} | [{meta.get('title')}]({rel(doc['path'])}) "
                             f"| {', '.join(meta.get('needs', []))} |")
            block.append("")
        untested = [d for d in m["findings"] if d["meta"].get("hardware_tested") == "no"]
        if untested:
            block += ["### Findings never run on real hardware", ""]
            block += [f"- [{d['meta'].get('title')}]({rel(d['path'])}) ({d['meta'].get('status')})" for d in untested]
            block.append("")
        weak = [(d, d.get("claim_tags", []).count("hypothesis") + d.get("claim_tags", []).count("open")) for d in m["findings"]]
        weak = [(d, n) for d, n in weak if n]
        if weak:
            block += ["### Findings that contain unproven claims", "",
                      "Each line counts the claims tagged `[hypothesis]` or `[open]` inside the finding.", ""]
            block += [f"- [{d['meta'].get('title')}]({rel(d['path'])}): {n}" for d, n in weak]
            block.append("")
        soft = [f for f in m["facts"] if f.get("status") in ("hypothesis", "open")]
        if soft:
            block += ["### Machine facts that are not established", ""]
            block += [f"- `{f.get('key')}` = {f.get('value')} ({f.get('status')})" for f in soft]
            block.append("")
        unhashed = [i for i in m["images"] if "sha256" not in i and not all("sha256" in p for p in i.get("part", [{}]))]
        if unhashed:
            block += ["### Firmware images without a complete SHA-256", ""]
            block += [f"- `{i.get('id')}`: {i.get('label')}" for i in unhashed]
            block.append("")
        if block:
            out += [f"## {m['meta'].get('name', mid)}", ""] + block
    return "\n".join(out).rstrip() + "\n"


def generated_files(data: dict) -> dict[str, str]:
    return {
        "index.json": json.dumps(build_index(data), indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        "STATUS.md": build_status(data),
        "GAPS.md": build_gaps(data),
    }


# --- commands: knowledge base -------------------------------------------------

def cmd_check(args: argparse.Namespace) -> int:
    problems = Problems()
    data = load_all(problems)
    validate(data, problems)
    if not problems.items:
        for name, text in generated_files(data).items():
            path = ROOT / name
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                problems.add(name, "out of date; run `python3 tools/oar.py build`")
    for item in problems.items:
        print("ERROR", item)
    counts = {m: (len(v["findings"]), len(v["questions"])) for m, v in data["machines"].items()}
    total_f = sum(c[0] for c in counts.values())
    total_q = sum(c[1] for c in counts.values())
    print(f"{len(counts)} machines, {total_f} findings, {total_q} open questions, {len(problems.items)} problems")
    return 1 if problems.items else 0


def cmd_build(args: argparse.Namespace) -> int:
    problems = Problems()
    data = load_all(problems)
    validate(data, problems)
    if problems.items:
        for item in problems.items:
            print("ERROR", item)
        print("fix these before building")
        return 1
    for name, text in generated_files(data).items():
        (ROOT / name).write_text(text, encoding="utf-8")
        print("wrote", name)
    return 0


def cmd_find(args: argparse.Namespace) -> int:
    data = load_all(Problems())
    words = [w.lower() for w in args.text]
    hits = 0
    for mid, machine in data["machines"].items():
        if args.machine and mid != args.machine:
            continue
        for kind in ("findings", "questions"):
            for doc in machine[kind]:
                meta = doc["meta"]
                if args.area and meta.get("area") != args.area:
                    continue
                if args.status and meta.get("status") not in args.status.split(","):
                    continue
                if args.firmware and args.firmware not in meta.get("firmware", []):
                    continue
                haystack = (json.dumps(meta) + doc["body"]).lower()
                if not all(w in haystack for w in words):
                    continue
                hits += 1
                print(f"[{meta.get('status'):<10}] {meta.get('id')}")
                print(f"             {meta.get('title')}")
                print(f"             {rel(doc['path'])}")
    if not hits:
        print("nothing matched. That means it is not documented here; see GAPS.md.")
    return 0


def cmd_symbol(args: argparse.Namespace) -> int:
    data = load_all(Problems())
    query = args.query.lower()
    hits = 0
    for mid, machine in data["machines"].items():
        if args.machine and mid != args.machine:
            continue
        for fw, table in machine["symbols"].items():
            if args.firmware and fw != args.firmware:
                continue
            for row in table["rows"]:
                if query in row["name"].lower() or query == row["address"].lower() \
                        or query == row["file_offset"].lower() or query in row["notes"].lower():
                    hits += 1
                    print(f"{fw}  {row['name']}  {row['kind']}  addr={row['address'] or '-'}  "
                          f"file={row['file_offset'] or '-'}  size={row['size'] or '-'}  [{row['status']}]")
                    print(f"    {row['notes']}  -> {row['finding']}")
    if not hits:
        print("no symbol matched. Do not guess an address; see GAPS.md.")
    return 0


# --- commands: images ---------------------------------------------------------

def digests(blob: bytes) -> dict[str, str]:
    return {"crc32": f"{zlib.crc32(blob) & 0xFFFFFFFF:08x}",
            "sha1": hashlib.sha1(blob).hexdigest(),
            "sha256": hashlib.sha256(blob).hexdigest()}


def interleave(even: bytes, odd: bytes) -> bytes:
    if len(even) != len(odd):
        raise SystemExit(f"the two files differ in size ({len(even)} and {len(odd)} bytes)")
    out = bytearray(len(even) * 2)
    out[0::2], out[1::2] = even, odd
    return bytes(out)


def all_images() -> list[tuple[str, dict]]:
    out = []
    for mdir in machine_dirs():
        ffile = mdir / "firmware.toml"
        if ffile.is_file():
            out += [(mdir.name, image) for image in load_toml(ffile).get("image", [])]
    return out


def find_image(firmware_id: str) -> dict:
    for _, image in all_images():
        if image.get("id") == firmware_id:
            return image
    raise SystemExit(f"unknown firmware id {firmware_id!r}; ids are listed in machines/*/firmware.toml")


def match(blob: bytes) -> list[str]:
    mine = digests(blob)
    hits = []
    for _, image in all_images():
        for holder, what in [(image, "whole image")] + [(p, f"part '{p.get('role')}'") for p in image.get("part", [])]:
            keys = [k for k in ("sha256", "sha1", "crc32") if k in holder]
            if keys and all(holder[k] == mine[k] for k in keys) and holder.get("size", len(blob)) == len(blob):
                hits.append(f"{image['id']} ({image.get('label')}): {what}, matched on {'+'.join(keys)}")
    return hits


def cmd_identify(args: argparse.Namespace) -> int:
    blobs = [(p, Path(p).read_bytes()) for p in args.files]
    found = False
    for name, blob in blobs:
        info = digests(blob)
        print(f"{name}: {len(blob)} bytes  crc32 {info['crc32']}  sha1 {info['sha1']}")
        print(f"    sha256 {info['sha256']}")
        hits = match(blob)
        found |= bool(hits)
        for hit in hits:
            print("    MATCH", hit)
        if not hits:
            print("    no match in the registry")
    if len(blobs) == 2 and len(blobs[0][1]) == len(blobs[1][1]):
        for label, a, b in (("first=even, second=odd", blobs[0][1], blobs[1][1]),
                            ("first=odd, second=even", blobs[1][1], blobs[0][1])):
            for hit in match(interleave(a, b)):
                found = True
                print(f"interleaved ({label}): MATCH {hit}")
    if not found:
        print("Unknown image. Findings keyed to a firmware id do not apply to it until its "
              "bytes are checked (see docs/agent-workflow.md, step 2).")
    return 0 if found else 2


def cmd_interleave(args: argparse.Namespace) -> int:
    out = interleave(Path(args.even).read_bytes(), Path(args.odd).read_bytes())
    Path(args.output).write_bytes(out)
    print(f"wrote {args.output}: {len(out)} bytes  sha256 {hashlib.sha256(out).hexdigest()}")
    return 0


def cmd_split(args: argparse.Namespace) -> int:
    blob = Path(args.image).read_bytes()
    if len(blob) % 2:
        raise SystemExit("image has an odd number of bytes")
    for path, part in ((args.even, blob[0::2]), (args.odd, blob[1::2])):
        Path(path).write_bytes(part)
        print(f"wrote {path}: {len(part)} bytes  sha256 {hashlib.sha256(part).hexdigest()}")
    return 0


def parse_int(text: str) -> int:
    return int(text, 0)


def cmd_pin(args: argparse.Namespace) -> int:
    blob = Path(args.image).read_bytes()
    if args.offset + args.length > len(blob):
        raise SystemExit("range runs past the end of the image")
    chunk = blob[args.offset:args.offset + args.length]
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow([f"0x{args.offset:05X}", args.length, hashlib.sha256(chunk).hexdigest(),
                     args.label, args.finding])
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    image = find_image(args.firmware)
    blob = Path(args.image).read_bytes()
    failures = 0
    if "sha256" in image:
        ok = hashlib.sha256(blob).hexdigest() == image["sha256"]
        print(("ok   " if ok else "FAIL ") + f"whole image sha256 ({len(blob)} bytes)")
        failures += not ok
    else:
        print("note the registry has no whole-image sha256 for this firmware")
    machine = args.firmware.split("-")[0]
    pins = MACHINES / machine / "pins" / f"{args.firmware}.csv"
    if not pins.is_file():
        print("note no pins recorded for this firmware")
    else:
        _, rows = read_csv(pins)
        for row in rows:
            offset, length = int(row["file_offset"], 16), int(row["length"])
            ok = hashlib.sha256(blob[offset:offset + length]).hexdigest() == row["sha256"]
            failures += not ok
            print(("ok   " if ok else "FAIL ") + f"{row['file_offset']} +{length:<7} {row['label']}  ({row['finding']})")
    if failures:
        print(f"{failures} check(s) failed: findings for {args.firmware} cannot be trusted for this image")
    else:
        print("image matches everything recorded for", args.firmware)
    return 1 if failures else 0


# --- commands: patches --------------------------------------------------------

def toml_string(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)


def cmd_patch_diff(args: argparse.Namespace) -> int:
    base, new = Path(args.base).read_bytes(), Path(args.modified).read_bytes()
    if len(base) != len(new):
        raise SystemExit("images differ in size; a patch manifest keeps the size")
    hunks, start = [], None
    for index in range(len(base) + 1):
        differs = index < len(base) and base[index] != new[index]
        if differs and start is None:
            start = index
        elif not differs and start is not None:
            hunks.append((start, index))
            start = None
    merged = hunks  # never merged: a manifest carries changed bytes only, no firmware bytes
    out = io.StringIO()
    out.write('format = "oar-patch-1"\n')
    out.write(f"name = {toml_string(args.name)}\n")
    out.write(f"firmware = {toml_string(args.firmware)}\n")
    out.write(f"description = {toml_string(args.description)}\n")
    out.write(f'base_sha256 = "{hashlib.sha256(base).hexdigest()}"\n')
    out.write(f'result_sha256 = "{hashlib.sha256(new).hexdigest()}"\n')
    for a, b in merged:
        out.write("\n[[hunk]]\n")
        out.write(f"offset = 0x{a:05X}\n")
        out.write(f"length = {b - a}\n")
        out.write(f'old_sha256 = "{hashlib.sha256(base[a:b]).hexdigest()}"\n')
        out.write(f'new = "{new[a:b].hex().upper()}"\n')
        out.write('why = ""\n')
    Path(args.output).write_text(out.getvalue(), encoding="utf-8")
    print(f"wrote {args.output}: {len(merged)} hunk(s), {sum(b - a for a, b in merged)} byte(s). "
          "Fill in each 'why'.")
    return 0


def apply_patch(manifest: dict, blob: bytes) -> bytes:
    if manifest.get("format") != "oar-patch-1":
        raise SystemExit("not an oar-patch-1 manifest")
    if hashlib.sha256(blob).hexdigest() != manifest.get("base_sha256"):
        raise SystemExit("the image is not the base this patch was made for (base_sha256 mismatch)")
    out = bytearray(blob)
    for number, hunk in enumerate(manifest.get("hunk", []), start=1):
        new = bytes.fromhex(hunk["new"])
        offset, length = hunk["offset"], hunk["length"]
        if len(new) != length:
            raise SystemExit(f"hunk {number}: 'new' holds {len(new)} bytes but length is {length}")
        if offset + length > len(blob):
            raise SystemExit(f"hunk {number}: runs past the end of the image")
        if hashlib.sha256(blob[offset:offset + length]).hexdigest() != hunk["old_sha256"]:
            raise SystemExit(f"hunk {number}: the bytes being replaced are not the expected ones")
        out[offset:offset + length] = new
    result = bytes(out)
    if "result_sha256" in manifest and hashlib.sha256(result).hexdigest() != manifest["result_sha256"]:
        raise SystemExit("patched image does not hash to result_sha256")
    return result


def cmd_patch_apply(args: argparse.Namespace) -> int:
    manifest = load_toml(Path(args.manifest))
    result = apply_patch(manifest, Path(args.image).read_bytes())
    Path(args.output).write_bytes(result)
    print(f"wrote {args.output}: {len(manifest.get('hunk', []))} hunk(s) applied  "
          f"sha256 {hashlib.sha256(result).hexdigest()}")
    return 0


# --- entry point --------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="oar", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="validate the knowledge base").set_defaults(func=cmd_check)
    sub.add_parser("build", help="regenerate index.json, STATUS.md, GAPS.md").set_defaults(func=cmd_build)

    p = sub.add_parser("find", help="search findings and open questions")
    p.add_argument("text", nargs="*", help="words that must all appear")
    p.add_argument("--machine")
    p.add_argument("--area", choices=AREAS)
    p.add_argument("--firmware")
    p.add_argument("--status", help="comma-separated, e.g. hardware,emulator,static")
    p.set_defaults(func=cmd_find)

    p = sub.add_parser("symbol", help="look up a named address")
    p.add_argument("query", help="part of a name, or an exact address / file offset")
    p.add_argument("--machine")
    p.add_argument("--firmware")
    p.set_defaults(func=cmd_symbol)

    p = sub.add_parser("identify", help="match a file or an EPROM pair against the registry")
    p.add_argument("files", nargs="+")
    p.set_defaults(func=cmd_identify)

    p = sub.add_parser("interleave", help="even + odd chip files -> linear image")
    p.add_argument("even")
    p.add_argument("odd")
    p.add_argument("-o", "--output", required=True)
    p.set_defaults(func=cmd_interleave)

    p = sub.add_parser("split", help="linear image -> even + odd chip files")
    p.add_argument("image")
    p.add_argument("--even", required=True)
    p.add_argument("--odd", required=True)
    p.set_defaults(func=cmd_split)

    p = sub.add_parser("pin", help="print a pins.csv row for a byte range")
    p.add_argument("image")
    p.add_argument("offset", type=parse_int)
    p.add_argument("length", type=parse_int)
    p.add_argument("--label", required=True)
    p.add_argument("--finding", required=True)
    p.set_defaults(func=cmd_pin)

    p = sub.add_parser("verify", help="check an image against the registry and its pins")
    p.add_argument("firmware", help="firmware id, e.g. mpc3000-v3.12")
    p.add_argument("image", help="linear image file")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("patch-diff", help="two images -> patch manifest")
    p.add_argument("base")
    p.add_argument("modified")
    p.add_argument("--firmware", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--description", default="")
    p.add_argument("-o", "--output", required=True)
    p.set_defaults(func=cmd_patch_diff)

    p = sub.add_parser("patch-apply", help="apply a patch manifest")
    p.add_argument("manifest")
    p.add_argument("image")
    p.add_argument("-o", "--output", required=True)
    p.set_defaults(func=cmd_patch_apply)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
