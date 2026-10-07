"""Check that the iOS Swift engine agrees with the Python engine on every date.

This compiles ``ios/ParityTool`` with ``swiftc`` and takes about a minute, so it
only runs when ``IGNIRE_SWIFT_PARITY=1`` is set (the macOS CI job sets it).
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from ignire_calendar import MAX_GREGORIAN_DATE, MIN_GREGORIAN_DATE, to_new_calendar

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    ROOT / "ios" / "IgnireCalendar" / "IgnireCalendarCore.swift",
    ROOT / "ios" / "ParityTool" / "main.swift",
)


@unittest.skipUnless(os.environ.get("IGNIRE_SWIFT_PARITY") == "1", "set IGNIRE_SWIFT_PARITY=1")
@unittest.skipUnless(shutil.which("swiftc"), "swiftc is not installed")
class SwiftParityTests(unittest.TestCase):
    def test_swift_engine_matches_python_engine_on_every_date(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "ignire-dump"
            subprocess.run(
                ["swiftc", "-O", *map(str, SOURCES), "-o", str(binary)], check=True
            )
            with subprocess.Popen(
                [str(binary)], stdout=subprocess.PIPE, text=True
            ) as process:
                assert process.stdout is not None
                current = MIN_GREGORIAN_DATE
                for line in process.stdout:
                    result = to_new_calendar(current)
                    expected = (
                        f"{current.isoformat()} {result.year} {result.month} "
                        f"{result.day} {result.day_of_year}\n"
                    )
                    if line != expected:
                        process.kill()
                        self.fail(f"Swift {line.strip()!r} != Python {expected.strip()!r}")
                    current += timedelta(days=1)
            self.assertEqual(process.returncode, 0)
            self.assertEqual(current, MAX_GREGORIAN_DATE + timedelta(days=1))


if __name__ == "__main__":
    unittest.main()
