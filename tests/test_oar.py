"""Tests for tools/oar.py. Run: python3 -m unittest discover -s tests"""

import contextlib
import hashlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import oar  # noqa: E402


def run(*argv: str) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = oar.main(list(argv))
    return code, out.getvalue()


class FrontMatter(unittest.TestCase):
    def test_parses_strings_and_arrays(self):
        meta, body = oar.parse_front_matter(
            '---\nid: m.x\ntitle: "A: B"\nfirmware: ["a", "b"]\n---\nbody\n')
        self.assertEqual(meta, {"id": "m.x", "title": "A: B", "firmware": ["a", "b"]})
        self.assertEqual(body, "body\n")

    def test_rejects_unquoted_colon(self):
        with self.assertRaises(ValueError):
            oar.parse_front_matter("---\ntitle: A: B\n---\n")

    def test_rejects_missing_close(self):
        with self.assertRaises(ValueError):
            oar.parse_front_matter("---\nid: x\n")

    def test_rejects_duplicate_key(self):
        with self.assertRaises(ValueError):
            oar.parse_front_matter("---\nid: x\nid: y\n---\n")


class Repository(unittest.TestCase):
    def test_knowledge_base_is_valid_and_generated_files_are_current(self):
        code, out = run("check")
        self.assertEqual(code, 0, out)

    def test_find_and_symbol(self):
        code, out = run("find", "floppy", "--machine", "mpc3000")
        self.assertEqual(code, 0)
        self.assertIn("mpc3000.floppy-sys-loader", out)
        code, out = run("symbol", "startup_loader", "--firmware", "mpc3000-v3.12")
        self.assertIn("B000:0141", out)

    def test_find_reports_absence(self):
        _, out = run("find", "zzz-no-such-thing")
        self.assertIn("not documented", out)

    def test_every_symbol_file_offset_follows_from_its_address(self):
        """ROM code symbols on the MPC3000: file = ((seg << 4) + off) & 0x7FFFF."""
        data = oar.load_all(oar.Problems())
        checked = 0
        for firmware, table in data["machines"]["mpc3000"]["symbols"].items():
            for row in table["rows"]:
                if row["kind"] not in ("code", "vector", "table") or not row["address"] or not row["file_offset"]:
                    continue
                seg, off = (int(part, 16) for part in row["address"].split(":"))
                if firmware == "mpc3000-v3.16-sys":
                    # Relative seg:off in the load image, which follows the 7A00h-byte MZ header.
                    expected = 0x7A00 + (seg << 4) + off
                else:
                    expected = ((seg << 4) + off) & 0x7FFFF
                self.assertEqual(expected, int(row["file_offset"], 16), f"{firmware} {row['name']}")
                checked += 1
        self.assertGreater(checked, 140)

    def test_mpc2000xl_runtime_addresses_equal_file_offsets(self):
        """OS 1.20 runs from a RAM copy where seg*16+off is the file offset."""
        data = oar.load_all(oar.Problems())
        checked = 0
        for row in data["machines"]["mpc2000xl"]["symbols"]["mpc2000xl-os1.20"]["rows"]:
            if not row["address"] or not row["file_offset"]:
                continue
            seg, off = (int(part, 16) for part in row["address"].split(":"))
            linear = (seg << 4) + off
            expected = linear - 0x80000 if linear >= 0x80000 else linear  # boot block: physical
            self.assertEqual(expected, int(row["file_offset"], 16), row["name"])
            checked += 1
        self.assertGreater(checked, 30)


class Images(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name: str, blob: bytes) -> str:
        path = self.dir / name
        path.write_bytes(blob)
        return str(path)

    def test_interleave_and_split_round_trip(self):
        even, odd = bytes(range(0, 200, 2)), bytes(range(1, 201, 2))
        linear = self.write("linear", b"")
        code, _ = run("interleave", self.write("even", even), self.write("odd", odd), "-o", linear)
        self.assertEqual(code, 0)
        self.assertEqual(Path(linear).read_bytes(), bytes(range(200)))
        run("split", linear, "--even", str(self.dir / "e2"), "--odd", str(self.dir / "o2"))
        self.assertEqual((self.dir / "e2").read_bytes(), even)
        self.assertEqual((self.dir / "o2").read_bytes(), odd)

    def test_identify_unknown_file(self):
        code, out = run("identify", self.write("x", b"not firmware"))
        self.assertEqual(code, 2)
        self.assertIn("Unknown image", out)

    def test_pin_row(self):
        blob = bytes(range(256))
        _, out = run("pin", self.write("img", blob), "0x10", "4", "--label", "four bytes", "--finding", "m.f")
        self.assertEqual(out.strip(), "0x00010,4," + hashlib.sha256(blob[16:20]).hexdigest() + ",four bytes,m.f")

    def test_patch_round_trip_carries_no_original_bytes(self):
        base = bytes([0x11] * 64)
        new = bytearray(base)
        new[5] = 0xEB
        new[40:43] = b"\x90\x90\x90"
        manifest = str(self.dir / "p.toml")
        run("patch-diff", self.write("base", base), self.write("new", bytes(new)),
            "--firmware", "mpc3000-v3.12", "--name", "t", "-o", manifest)
        text = Path(manifest).read_text()
        self.assertEqual(text.count("[[hunk]]"), 2)
        self.assertNotIn('"11', text)                      # no base bytes in the manifest
        out_path = str(self.dir / "out")
        code, _ = run("patch-apply", manifest, str(self.dir / "base"), "-o", out_path)
        self.assertEqual(code, 0)
        self.assertEqual(Path(out_path).read_bytes(), bytes(new))

    def test_patch_refuses_wrong_base(self):
        base = bytes(64)
        new = bytearray(base)
        new[1] = 1
        manifest = str(self.dir / "p.toml")
        run("patch-diff", self.write("base", base), self.write("new", bytes(new)),
            "--firmware", "x", "--name", "t", "-o", manifest)
        with self.assertRaises(SystemExit):
            run("patch-apply", manifest, self.write("other", bytes([1] * 64)), "-o", str(self.dir / "o"))


if __name__ == "__main__":
    unittest.main()
