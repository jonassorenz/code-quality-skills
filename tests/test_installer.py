from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CLI = REPO_ROOT / "bin" / "cli.js"


class InstallerTests(unittest.TestCase):
    def install(self, working_directory: Path, skill: str) -> Path:
        result = subprocess.run(
            [
                "node",
                str(CLI),
                "install",
                skill,
                "--agent",
                "agents",
                "--scope",
                "project",
            ],
            cwd=working_directory,
            check=True,
            capture_output=True,
            text=True,
        )
        target = working_directory / ".agents" / "skills" / skill
        self.assertIn(str(target), result.stdout)
        return target

    def test_installs_complete_runtime_packages_without_readmes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            working_directory = Path(temp)
            feature = self.install(working_directory, "feature-gap-auditor")
            production = self.install(working_directory, "production-gap-auditor")

            self.assertTrue((feature / "agents" / "openai.yaml").is_file())
            self.assertTrue(
                (feature / "references" / "runtime-verification.md").is_file()
            )
            self.assertFalse((feature / "README.md").exists())

            scanner = production / "scripts" / "scan_candidates.py"
            self.assertTrue(scanner.is_file())
            self.assertTrue(os.access(scanner, os.X_OK))
            self.assertTrue(
                (
                    production
                    / "references"
                    / "platform-risk-checklists.md"
                ).is_file()
            )
            self.assertFalse((production / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
