#!/usr/bin/env python3
"""Build deterministic .skill archives for the audit skills."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = {
    "feature-gap-auditor": REPO_ROOT / "feature-gap-auditor-skill",
    "production-gap-auditor": REPO_ROOT / "production-gap-auditor-skill",
}
INCLUDED_ROOTS = {"SKILL.md", "agents", "references", "scripts"}
FIXED_TIMESTAMP = (2020, 1, 1, 0, 0, 0)


def source_files(skill_dir: Path) -> list[Path]:
    files = []
    for path in skill_dir.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(skill_dir)
        if relative.parts[0] not in INCLUDED_ROOTS:
            continue
        if "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(skill_dir).as_posix())


def build_archive(skill_name: str, skill_dir: Path) -> Path:
    archive = skill_dir / f"{skill_name}.skill"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED, compresslevel=9) as output:
        for path in source_files(skill_dir):
            relative = path.relative_to(skill_dir)
            archive_name = f"{skill_name}/{relative.as_posix()}"
            info = ZipInfo(archive_name, date_time=FIXED_TIMESTAMP)
            info.compress_type = ZIP_DEFLATED
            mode = 0o755 if relative.parts[0] == "scripts" else 0o644
            info.external_attr = mode << 16
            output.writestr(info, path.read_bytes(), compress_type=ZIP_DEFLATED, compresslevel=9)
    return archive


def main() -> int:
    for skill_name, skill_dir in SKILLS.items():
        archive = build_archive(skill_name, skill_dir)
        print(archive.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
