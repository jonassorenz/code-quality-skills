#!/usr/bin/env python3
"""Generate deterministic static audit candidates.

The output is intentionally E0 evidence: every hit requires execution-path tracing and
verification before it can become an audit finding.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Pattern


EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".next",
    ".nuxt",
    ".svn",
    ".turbo",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "deriveddata",
    "dist",
    "generated",
    "node_modules",
    "pods",
    "target",
    "vendor",
    "venv",
}

TEST_DIRS = {
    "__snapshots__",
    "__tests__",
    "e2e",
    "evals",
    "fixtures",
    "mocks",
    "snapshots",
    "test",
    "tests",
}

SOURCE_SUFFIXES = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".css",
    ".dart",
    ".env",
    ".go",
    ".graphql",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".kts",
    ".m",
    ".mm",
    ".php",
    ".prisma",
    ".py",
    ".rb",
    ".rs",
    ".scss",
    ".sh",
    ".sql",
    ".swift",
    ".toml",
    ".ts",
    ".tsx",
    ".vue",
    ".xml",
    ".yaml",
    ".yml",
}

SOURCE_NAMES = {
    "Dockerfile",
    "Gemfile",
    "Makefile",
    "Podfile",
    "Procfile",
}

MAX_FILE_BYTES = 2 * 1024 * 1024

SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}"),
)


@dataclass(frozen=True)
class Rule:
    identifier: str
    category: str
    pattern: Pattern[str]


RULES = (
    Rule(
        "silent.empty-catch",
        "silent-failure",
        re.compile(r"catch\s*\([^)]*\)\s*\{\s*\}", re.MULTILINE),
    ),
    Rule(
        "silent.empty-promise-catch",
        "silent-failure",
        re.compile(r"\.catch\s*\(\s*\(\s*\)\s*=>\s*\{\s*\}\s*\)", re.MULTILINE),
    ),
    Rule(
        "silent.log-only-catch",
        "silent-failure",
        re.compile(
            r"catch\s*\([^)]*\)\s*\{\s*console\.(?:log|warn|error)\s*"
            r"\([^{};]*\)\s*;?\s*\}",
            re.MULTILINE,
        ),
    ),
    Rule(
        "silent.python-except-pass",
        "silent-failure",
        re.compile(r"except(?:\s+[^:\n]+)?\s*:\s*(?:#.*\n\s*)?pass\b", re.MULTILINE),
    ),
    Rule(
        "incomplete.marker",
        "incomplete",
        re.compile(r"\b(?:TODO|FIXME|HACK|XXX|NOCOMMIT|STOPSHIP)\b"),
    ),
    Rule(
        "incomplete.not-implemented",
        "incomplete",
        re.compile(
            r"NotImplemented(?:Error|Exception)|not[ _-]?implemented|todo!\(\)|unimplemented!\(\)",
            re.IGNORECASE,
        ),
    ),
    Rule(
        "incomplete.placeholder",
        "incomplete",
        re.compile(
            r"lorem ipsum|test@example\.com|changeme|your-api-key|sk-xxx|pk_test",
            re.IGNORECASE,
        ),
    ),
    Rule(
        "security.client-token-storage",
        "security",
        re.compile(
            r"localStorage\.(?:setItem|getItem)\s*\([^)]*(?:token|auth|session|secret|jwt|credential)",
            re.IGNORECASE,
        ),
    ),
    Rule(
        "security.wildcard-cors",
        "security",
        re.compile(r"Access-Control-Allow-Origin[^,\n]*\*|allow_origin[s]?\s*[:=]\s*[\"']\*[\"']", re.IGNORECASE),
    ),
    Rule(
        "ux.generic-error-copy",
        "ux-recovery",
        re.compile(r"Something went wrong|An error occurred|Unknown error|Unexpected error"),
    ),
    Rule(
        "state.timer-or-listener",
        "state-lifecycle",
        re.compile(r"\b(?:setInterval|addEventListener|NotificationCenter\.default\.addObserver)\b"),
    ),
    Rule(
        "integration.environment-reference",
        "integration",
        re.compile(
            r"process\.env\.|import\.meta\.env\.|os\.(?:environ|getenv)|env::var|System\.getenv"
        ),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="Repository root to scan")
    parser.add_argument("--format", choices=("text", "jsonl"), default="text")
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include test, fixture, mock, and snapshot paths",
    )
    parser.add_argument(
        "--max-per-rule",
        type=int,
        default=100,
        help="Maximum candidates emitted for each rule (default: 100)",
    )
    return parser.parse_args()


def is_test_path(path: Path) -> bool:
    lower_parts = {part.lower() for part in path.parts}
    lower_name = path.name.lower()
    return bool(lower_parts & TEST_DIRS) or any(
        marker in lower_name
        for marker in (".test.", ".tests.", ".spec.", "_test.", "_spec.")
    )


def is_source_file(path: Path) -> bool:
    return path.name in SOURCE_NAMES or path.suffix.lower() in SOURCE_SUFFIXES


def iter_source_files(root: Path, include_tests: bool) -> Iterable[Path]:
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        lower_parts = {part.lower() for part in relative.parts[:-1]}
        if lower_parts & EXCLUDED_DIRS:
            continue
        if not include_tests and is_test_path(relative):
            continue
        if not is_source_file(path):
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
        except OSError:
            continue
        yield path


def read_text(path: Path) -> Optional[str]:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in data:
        return None
    return data.decode("utf-8", errors="replace")


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def safe_excerpt(text: str, offset: int) -> str:
    start = text.rfind("\n", 0, offset) + 1
    end = text.find("\n", offset)
    if end == -1:
        end = len(text)
    excerpt = re.sub(r"\s+", " ", text[start:end]).strip()
    for pattern in SECRET_PATTERNS:
        excerpt = pattern.sub("[REDACTED]", excerpt)
    if len(excerpt) > 220:
        excerpt = f"{excerpt[:217]}..."
    return excerpt


def scan(root: Path, include_tests: bool, max_per_rule: int) -> list[dict[str, object]]:
    counts = {rule.identifier: 0 for rule in RULES}
    candidates: list[dict[str, object]] = []
    seen: set[tuple[str, str, int]] = set()
    scanner_path = Path(__file__).resolve()

    for path in iter_source_files(root, include_tests):
        if path.resolve() == scanner_path:
            continue
        text = read_text(path)
        if text is None:
            continue
        relative = path.relative_to(root).as_posix()
        for rule in RULES:
            if counts[rule.identifier] >= max_per_rule:
                continue
            for match in rule.pattern.finditer(text):
                if counts[rule.identifier] >= max_per_rule:
                    break
                candidate_line = line_number(text, match.start())
                key = (rule.identifier, relative, candidate_line)
                if key in seen:
                    continue
                seen.add(key)
                candidates.append(
                    {
                        "evidence": "E0",
                        "category": rule.category,
                        "rule": rule.identifier,
                        "path": relative,
                        "line": candidate_line,
                        "excerpt": safe_excerpt(text, match.start()),
                    }
                )
                counts[rule.identifier] += 1

    return sorted(
        candidates,
        key=lambda item: (
            str(item["path"]),
            int(item["line"]),
            str(item["rule"]),
        ),
    )


def emit(candidates: list[dict[str, object]], output_format: str) -> None:
    if output_format == "jsonl":
        for candidate in candidates:
            print(json.dumps(candidate, sort_keys=True))
        return

    print("E0 candidates only — trace and verify before reporting")
    for candidate in candidates:
        print(
            f"{candidate['path']}:{candidate['line']} "
            f"[{candidate['category']}/{candidate['rule']}] {candidate['excerpt']}"
        )
    print(f"candidate_count={len(candidates)}")


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"error: scan root is not a directory: {root}", file=sys.stderr)
        return 2
    if args.max_per_rule < 1:
        print("error: --max-per-rule must be at least 1", file=sys.stderr)
        return 2
    emit(scan(root, args.include_tests, args.max_per_rule), args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
