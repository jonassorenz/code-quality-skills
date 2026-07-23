from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCANNER = (
    REPO_ROOT
    / "production-gap-auditor-skill"
    / "scripts"
    / "scan_candidates.py"
)


class ScanCandidatesTests(unittest.TestCase):
    def run_scanner(self, root: Path, *extra: str) -> list[dict[str, object]]:
        result = subprocess.run(
            [sys.executable, str(SCANNER), str(root), "--format", "jsonl", *extra],
            check=True,
            capture_output=True,
            text=True,
        )
        return [json.loads(line) for line in result.stdout.splitlines() if line]

    def test_finds_multiline_candidates_and_excludes_tests(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "src"
            tests = root / "tests"
            source.mkdir()
            tests.mkdir()
            (source / "app.ts").write_text(
                """
                // TODO: replace placeholder
                try {
                  run();
                } catch (error) {
                }
                try {
                  await save();
                } catch (error) {
                  console.error(error);
                }
                localStorage.setItem("auth_token", value);
                """,
                encoding="utf-8",
            )
            (tests / "app.test.ts").write_text(
                "// STOPSHIP should be excluded by default\n",
                encoding="utf-8",
            )

            candidates = self.run_scanner(root)
            rules = {candidate["rule"] for candidate in candidates}
            paths = {candidate["path"] for candidate in candidates}

            self.assertIn("incomplete.marker", rules)
            self.assertIn("silent.empty-catch", rules)
            self.assertIn("silent.log-only-catch", rules)
            self.assertIn("security.client-token-storage", rules)
            self.assertEqual(paths, {"src/app.ts"})

    def test_include_tests_and_limit_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            tests = root / "tests"
            tests.mkdir()
            (tests / "first.test.ts").write_text("// TODO one\n", encoding="utf-8")
            (tests / "second.test.ts").write_text("// TODO two\n", encoding="utf-8")

            candidates = self.run_scanner(
                root,
                "--include-tests",
                "--max-per-rule",
                "1",
            )

            markers = [
                candidate
                for candidate in candidates
                if candidate["rule"] == "incomplete.marker"
            ]
            self.assertEqual(len(markers), 1)
            self.assertEqual(markers[0]["path"], "tests/first.test.ts")

    def test_rejects_invalid_root(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCANNER), "/definitely/missing/audit-root"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("scan root is not a directory", result.stderr)

    def test_redacts_credential_shaped_excerpts(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "app.ts"
            credential = "sk-" + "abcdefghijklmnopqrstuvwx"
            source.write_text(
                f"// TODO rotate {credential}\n",
                encoding="utf-8",
            )

            candidates = self.run_scanner(root)
            marker = next(
                candidate
                for candidate in candidates
                if candidate["rule"] == "incomplete.marker"
            )

            self.assertIn("[REDACTED]", marker["excerpt"])
            self.assertNotIn(credential, marker["excerpt"])


if __name__ == "__main__":
    unittest.main()
