"""Tests for machines/mpc2000xl/tools/xlimage.py, on synthetic images."""

import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "machines" / "mpc2000xl" / "tools"))
import xlimage  # noqa: E402


def synthetic() -> bytes:
    image = bytearray(range(256)) * (xlimage.IMAGE_SIZE // 256)
    struct.pack_into("<I", image, xlimage.MAGIC_POINTER, 0x461)
    image[0x461:0x461 + 9] = xlimage.MAGIC
    return xlimage.fix_checksum(bytes(image))


class Checks(unittest.TestCase):
    def test_valid_image(self):
        self.assertEqual(xlimage.problems(synthetic()), [])

    def test_stale_checksum(self):
        image = bytearray(synthetic())
        image[0x30E43] ^= 0xFF
        self.assertTrue(any("checksum" in p for p in xlimage.problems(bytes(image))))
        self.assertEqual(xlimage.problems(xlimage.fix_checksum(bytes(image))), [])

    def test_bytes_past_the_sum_do_not_count(self):
        image = bytearray(synthetic())
        image[0x7C000] ^= 0xFF
        self.assertEqual(xlimage.word_sum(bytes(image)), xlimage.word_sum(synthetic()))

    def test_missing_magic(self):
        image = bytearray(synthetic())
        image[0x461] = 0
        self.assertTrue(any("magic" in p for p in xlimage.problems(xlimage.fix_checksum(bytes(image)))))

    def test_wrong_size(self):
        self.assertTrue(xlimage.problems(b"\0" * 100))


class Compare(unittest.TestCase):
    def test_body_change_is_accepted(self):
        stock = synthetic()
        image = bytearray(stock)
        image[0x30E43:0x30E4A] = b"1.2 PM "
        errors, notes = xlimage.compare(stock, xlimage.fix_checksum(bytes(image)))
        self.assertEqual(errors, [])

    def test_protected_ranges_are_refused(self):
        stock = synthetic()
        for offset in (0x10040, 0x25BE0, 0x79000, 0x7FFF0):
            image = bytearray(stock)
            image[offset] ^= 0xFF
            errors, _ = xlimage.compare(stock, xlimage.fix_checksum(bytes(image)))
            self.assertTrue(errors, hex(offset))


if __name__ == "__main__":
    unittest.main()
