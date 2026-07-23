from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = (
    REPO_ROOT / "feature-gap-auditor-skill" / "SKILL.md",
    REPO_ROOT / "production-gap-auditor-skill" / "SKILL.md",
)

NO_FINDINGS = (
    "No confirmed gaps were found within the audited scope and achieved evidence level."
)
INCOMPLETE = "No confirmed gaps have been found yet; audit coverage remains incomplete."
NO_OPEN = (
    "No open confirmed gaps remain within the audited scope and achieved evidence level."
)


class ZeroFindingsContractTests(unittest.TestCase):
    def test_both_skills_define_bounded_zero_findings_verdicts(self) -> None:
        for skill_path in SKILLS:
            text = skill_path.read_text(encoding="utf-8")

            self.assertIn("### Zero-findings verdict", text)
            self.assertIn(NO_FINDINGS, text)
            self.assertIn(INCOMPLETE, text)
            self.assertIn(NO_OPEN, text)
            self.assertIn("highest evidence level", text)
            self.assertIn("blocked", text)
            self.assertIn("unverified", text)
            self.assertIn("bug-free", text)


if __name__ == "__main__":
    unittest.main()
