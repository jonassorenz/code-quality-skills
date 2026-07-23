from __future__ import annotations

import unittest
from pathlib import Path
from zipfile import ZipFile


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = {
    "feature-gap-auditor": REPO_ROOT / "feature-gap-auditor-skill",
    "production-gap-auditor": REPO_ROOT / "production-gap-auditor-skill",
}
INCLUDED_ROOTS = {"SKILL.md", "agents", "references", "scripts"}


class SkillPackageTests(unittest.TestCase):
    def test_archives_match_source_files(self) -> None:
        for skill_name, skill_dir in SKILLS.items():
            archive = skill_dir / f"{skill_name}.skill"
            self.assertTrue(archive.exists(), archive)

            expected = {}
            for path in skill_dir.rglob("*"):
                if not path.is_file():
                    continue
                relative = path.relative_to(skill_dir)
                if relative.parts[0] not in INCLUDED_ROOTS:
                    continue
                if "__pycache__" in relative.parts or path.suffix == ".pyc":
                    continue
                expected[f"{skill_name}/{relative.as_posix()}"] = path.read_bytes()

            with ZipFile(archive) as package:
                actual_names = {
                    name for name in package.namelist() if not name.endswith("/")
                }
                self.assertEqual(actual_names, set(expected))
                for name, content in expected.items():
                    self.assertEqual(package.read(name), content, name)


if __name__ == "__main__":
    unittest.main()
