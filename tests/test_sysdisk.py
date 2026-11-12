"""Tests for machines/mpc3000/tools/sysdisk.py."""

import hashlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "machines" / "mpc3000" / "tools"))
import sysdisk  # noqa: E402


class Hello(unittest.TestCase):
    def test_reproduces_the_disk_image_run_on_hardware(self):
        """The test program that ran on a physical MPC3000 on 2026-10-01 printed
        this marker text and was packed with these labels. Building it again
        must give the same 1.44M image, byte for byte."""
        payload = sysdisk.pack_mz(sysdisk.hello_image(b"Vailixi 3.51 (---/--/----)"))
        self.assertEqual(len(payload), 288)
        disk = sysdisk.pack_fat12([("STARTUP.SYS", payload)], oem=b"MPC3KCAN",
                                  volume_id=b"\x50\x35\x43\x4E", label=b"VAILIXI350 ")
        self.assertEqual(hashlib.sha256(disk).hexdigest(),
                         "ce025a0cae336acc8c91e1a073f4008159e3c17e0f87b61a7d9784c68ad59b58")

    def test_hello_passes_the_loader_rules(self):
        errors, _ = sysdisk.inspect_mz(sysdisk.pack_mz(sysdisk.hello_image(b"HELLO FROM RAM")))
        self.assertEqual(errors, [])

    def test_text_limits(self):
        with self.assertRaises(ValueError):
            sysdisk.hello_image(b"x" * 200)
        with self.assertRaises(ValueError):
            sysdisk.hello_image(b"tab\there")


class Rules(unittest.TestCase):
    def test_rejects_non_mz(self):
        errors, _ = sysdisk.inspect_mz(b"ZM" + bytes(64))
        self.assertTrue(errors)

    def test_rejects_wrong_size_fields(self):
        blob = bytearray(sysdisk.pack_mz(bytes(100)))
        blob += b"\x00" * 7
        errors, _ = sysdisk.inspect_mz(bytes(blob))
        self.assertTrue(any("e_cp" in e for e in errors))

    def test_rejects_image_that_runs_into_page_61(self):
        errors, _ = sysdisk.inspect_mz(sysdisk.pack_mz(bytes(560_000)))
        self.assertTrue(any("3.08 / 3.11" in e for e in errors))      # too big from 0x70000
        self.assertFalse(any("3.12 / 3.50" in e for e in errors))     # still fits from 0x69000


class Disk(unittest.TestCase):
    def test_files_read_back_in_order(self):
        files = [("FIRST.SYS", sysdisk.pack_mz(bytes(700))), ("NOTES.TXT", b"hello"), ("BIG.DAT", bytes(range(256)) * 20)]
        disk = sysdisk.pack_fat12(files)
        self.assertEqual(len(disk), 1_474_560)
        self.assertEqual(sysdisk.read_root(disk), files)
        self.assertEqual(disk[11:32], sysdisk.BPB)
        self.assertEqual(disk[510:512], b"\x55\xAA")

    def test_fat_chain(self):
        disk = sysdisk.pack_fat12([("A.SYS", bytes(1025))])       # three clusters: 2 -> 3 -> 4 -> end
        fat = disk[512:512 + 9 * 512]

        def entry(n):
            pair = fat[n + n // 2] | fat[n + n // 2 + 1] << 8
            return pair >> 4 if n & 1 else pair & 0xFFF

        self.assertEqual([entry(2), entry(3), entry(4), entry(5)], [3, 4, 0xFFF, 0])

    def test_rejects_long_names(self):
        with self.assertRaises(ValueError):
            sysdisk.pack_fat12([("TOOLONGNAME.SYS", b"x")])


if __name__ == "__main__":
    unittest.main()
