#!/usr/bin/env python3
"""Scan a skill repository for common privacy and secret-leak patterns.

This scanner is intentionally conservative and cannot detect re-identification
through combinations of otherwise ordinary details. Complete the manual review
in references/privacy-release.md before publishing.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


TEXT_EXTENSIONS = {
    ".cfg", ".csv", ".ini", ".json", ".md", ".py", ".rst", ".toml",
    ".txt", ".yaml", ".yml",
}
EXCLUDED_DIRS = {".git", ".idea", ".pytest_cache", ".venv", "__pycache__"}
SEVERITY = {"low": 1, "medium": 2, "high": 3}
NOREPLY_EMAIL = re.compile(r"(?i)(?:noreply@github\.com|[^@]+@users\.noreply\.github\.com)$")


@dataclass(frozen=True)
class Rule:
    name: str
    severity: str
    pattern: re.Pattern[str]
    reason: str


RULES = (
    Rule(
        "windows-user-path",
        "high",
        re.compile(r"(?i)(?<![A-Za-z0-9])[A-Z]:\\(?:Users|Documents and Settings)\\[^\s<>\"|?*]+"),
        "Local user-profile paths can reveal account names and private layout.",
    ),
    Rule(
        "email-address",
        "high",
        re.compile(r"(?i)(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+"),
        "Email addresses are direct identifiers.",
    ),
    Rule(
        "mainland-mobile-number",
        "high",
        re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"),
        "Mobile numbers are direct identifiers.",
    ),
    Rule(
        "national-id-like-number",
        "high",
        re.compile(r"(?<!\d)\d{17}[0-9Xx](?!\d)"),
        "Long identity-number patterns require review.",
    ),
    Rule(
        "credential-token",
        "high",
        re.compile(r"(?i)(?:gh[opsu]_[A-Za-z0-9]{20,}|(?:api[_-]?key|token|secret)\s*[:=]\s*[\"']?[A-Za-z0-9_./+=-]{16,})"),
        "Credentials and access tokens must never be published.",
    ),
    Rule(
        "private-key-header",
        "high",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        "Private keys must never be published.",
    ),
    Rule(
        "ipv4-address",
        "medium",
        re.compile(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)"),
        "Network addresses may identify a private environment.",
    ),
    Rule(
        "url-sensitive-query",
        "high",
        re.compile(r"(?i)https?://[^\s]+[?&](?:access_token|api_key|key|signature|sig|token)=[^\s&#]+"),
        "URLs can embed credentials or signed access parameters.",
    ),
)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str
    severity: str
    reason: str
    excerpt: str


def iter_text_files(root: Path):
    candidates = [root] if root.is_file() else root.rglob("*")
    for path in candidates:
        if not path.is_file():
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        yield path


def read_denylist(path: Path | None) -> list[str]:
    if path is None:
        return []
    terms = []
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        term = raw.strip()
        if term and not term.startswith("#"):
            terms.append(term)
    return terms


def redact_excerpt(line: str, start: int, end: int) -> str:
    left = max(0, start - 32)
    right = min(len(line), end + 32)
    excerpt = line[left:start] + "[REDACTED]" + line[end:right]
    return excerpt.strip().replace("\t", " ")[:180]


def scan_file(path: Path, root: Path, denylist: list[str]) -> list[Finding]:
    try:
        content = path.read_text(encoding="utf-8-sig")
    except (UnicodeDecodeError, OSError):
        return []

    findings: list[Finding] = []
    for line_no, line in enumerate(content.splitlines(), 1):
        for rule in RULES:
            for match in rule.pattern.finditer(line):
                findings.append(
                    Finding(
                        str(path.relative_to(root) if root.is_dir() else path.name),
                        line_no,
                        rule.name,
                        rule.severity,
                        rule.reason,
                        redact_excerpt(line, match.start(), match.end()),
                    )
                )
        lowered = line.casefold()
        for index, term in enumerate(denylist, 1):
            start = lowered.find(term.casefold())
            if start >= 0:
                findings.append(
                    Finding(
                        str(path.relative_to(root) if root.is_dir() else path.name),
                        line_no,
                        f"custom-denylist-{index}",
                        "high",
                        "A caller-supplied private term was found.",
                        redact_excerpt(line, start, start + len(term)),
                    )
                )
    return findings


def scan_git_metadata(root: Path) -> list[Finding]:
    repo = root if root.is_dir() else root.parent
    result = subprocess.run(
        [
            "git", "-C", str(repo), "log", "--all",
            "--format=%H%x00%ae%x00%ce",
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return []

    findings: list[Finding] = []
    for line in result.stdout.splitlines():
        parts = line.split("\0")
        if len(parts) != 3:
            continue
        commit, author_email, committer_email = parts
        for role, email in (("author", author_email), ("committer", committer_email)):
            if email and not NOREPLY_EMAIL.fullmatch(email):
                findings.append(
                    Finding(
                        ".git/commit-metadata",
                        0,
                        f"git-{role}-email",
                        "high",
                        "Git commit metadata exposes a non-noreply email address.",
                        f"[REDACTED] in commit {commit[:12]}",
                    )
                )
    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", help="File or directory to scan")
    parser.add_argument(
        "--denylist",
        type=Path,
        help="External UTF-8 file with one private literal per line; keep it outside the repository",
    )
    parser.add_argument(
        "--fail-on",
        choices=("none", "medium", "high"),
        default="high",
        help="Return exit code 2 when findings meet this severity (default: high)",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument(
        "--git-metadata",
        action="store_true",
        help="Also flag non-noreply author and committer emails in Git history",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.path).resolve()
    if not root.exists():
        print(f"Path does not exist: {root}", file=sys.stderr)
        return 1
    if args.denylist and not args.denylist.is_file():
        print(f"Denylist does not exist: {args.denylist}", file=sys.stderr)
        return 1

    denylist = read_denylist(args.denylist)
    files = list(iter_text_files(root))
    findings = [item for path in files for item in scan_file(path, root, denylist)]
    if args.git_metadata:
        findings.extend(scan_git_metadata(root))

    if args.json:
        print(json.dumps({"files_scanned": len(files), "findings": [asdict(f) for f in findings]}, indent=2))
    else:
        print(f"Scanned {len(files)} text files; findings: {len(findings)}")
        for finding in findings:
            print(
                f"{finding.severity.upper()} {finding.path}:{finding.line} "
                f"[{finding.rule}] {finding.excerpt}"
            )

    if args.fail_on == "none":
        return 0
    threshold = SEVERITY[args.fail_on]
    return 2 if any(SEVERITY[f.severity] >= threshold for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
