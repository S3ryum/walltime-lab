"""Integration tests for the command-line entry point."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest


class CliTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "walltime_lab", *arguments],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_human_output_explains_both_kinds_of_wall_time_change(self) -> None:
        result = self.run_cli("Europe/Amsterdam", "2024")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("skipped 2024-03-31 02:00:00–2024-03-31 03:00:00", result.stdout)
        self.assertIn("repeated 2024-10-27 02:00:00–2024-10-27 03:00:00", result.stdout)

    def test_json_output_is_machine_readable(self) -> None:
        result = self.run_cli("Europe/Amsterdam", "2024", "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["zone"], "Europe/Amsterdam")
        self.assertEqual(payload["year"], 2024)
        self.assertEqual(
            [row["kind"] for row in payload["transitions"]],
            ["gap", "overlap"],
        )

    def test_invalid_zone_exits_with_actionable_error(self) -> None:
        result = self.run_cli("Mars/Olympus", "2026")

        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown IANA time zone", result.stderr)

    def test_help_and_version(self) -> None:
        help_result = self.run_cli("--help")
        version_result = self.run_cli("--version")

        self.assertEqual(help_result.returncode, 0)
        self.assertIn("IANA zone", help_result.stdout)
        self.assertEqual(version_result.returncode, 0)
        self.assertIn("walltime-lab 0.1.0", version_result.stdout)


if __name__ == "__main__":
    unittest.main()
