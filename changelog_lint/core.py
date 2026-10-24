"""Keep a Changelog validator: headings, section names, version order, dates and links. Offline."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

SECTIONS = ("Added", "Changed", "Deprecated", "Removed", "Fixed", "Security")
VERSION_HEADING_RE = re.compile(r"^##\s+\[(?P<ver>[^\]]+)\](?:\s+-\s+(?P<date>\S+))?\s*$")
UNRELEASED_RE = re.compile(r"^##\s+\[Unreleased\]\s*$", re.IGNORECASE)
SECTION_RE = re.compile(r"^###\s+(?P<name>.+?)\s*$")
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
LINK_DEF_RE = re.compile(r"^\[(?P<ver>[^\]]+)\]:\s+\S+")
FENCE_OPEN_RE = re.compile(r"^\s*(?P<fence>`{3,}|~{3,}).*$")
FENCE_CLOSE_RE = re.compile(r"^\s*(?P<fence>`{3,}|~{3,})\s*$")


@dataclass(frozen=True)
class Finding:
    level: str  # error | warning
    code: str
    line: int
    message: str


def _semver_key(version: str) -> tuple[int, int, int, int, tuple[tuple[int, int | str], ...]]:
    # Build metadata is valid SemVer but must not affect precedence.
    precedence = version.partition("+")[0]
    core, separator, prerelease = precedence.partition("-")
    major, minor, patch = (int(part) for part in core.split("."))
    if not separator:
        return major, minor, patch, 1, ()
    identifiers = tuple(
        (0, int(part)) if part.isdigit() else (1, part)
        for part in prerelease.split(".")
    )
    return major, minor, patch, 0, identifiers


def lint(text: str, today: date | None = None) -> list[Finding]:
    today = today or date.today()
    findings: list[Finding] = []
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        findings.append(Finding("error", "NO_TITLE", 1, "file must start with a '# Changelog' title"))

    versions: list[tuple[int, str]] = []
    unreleased_seen = 0
    current_section_line = None
    in_release = False
    section_names: list[str] = []
    fence_char = None
    fence_length = 0
    content_lines: list[str] = []
    for number, line in enumerate(lines, start=1):
        if fence_char is not None:
            closing = FENCE_CLOSE_RE.match(line)
            if closing and closing.group("fence")[0] == fence_char and len(closing.group("fence")) >= fence_length:
                fence_char = None
                fence_length = 0
            content_lines.append("")
            continue
        opening = FENCE_OPEN_RE.match(line)
        if opening:
            fence_char = opening.group("fence")[0]
            fence_length = len(opening.group("fence"))
            content_lines.append("")
            continue
        content_lines.append(line)
        if line.startswith("## "):
            if in_release:
                _check_sections(findings, section_names, current_section_line)
            section_names = []
            in_release = True
            if UNRELEASED_RE.match(line):
                unreleased_seen += 1
                continue
            match = VERSION_HEADING_RE.match(line)
            if not match:
                findings.append(Finding("error", "BAD_HEADING", number, f"unrecognised release heading: {line.strip()}"))
                continue
            ver, dt = match.group("ver"), match.group("date")
            if not SEMVER_RE.match(ver):
                findings.append(Finding("warning", "NON_SEMVER", number, f"version {ver!r} is not MAJOR.MINOR.PATCH"))
            else:
                versions.append((number, ver))
            if dt is None:
                findings.append(Finding("warning", "MISSING_DATE", number, f"release {ver} has no date"))
            else:
                try:
                    parsed = date.fromisoformat(dt)
                    if parsed > today:
                        findings.append(Finding("error", "FUTURE_DATE", number, f"release {ver} is dated in the future ({dt})"))
                except ValueError:
                    findings.append(Finding("error", "BAD_DATE", number, f"release {ver} date {dt!r} is not YYYY-MM-DD"))
            current_section_line = number
        elif line.startswith("### ") and in_release:
            match = SECTION_RE.match(line)
            name = match.group("name") if match else ""
            if name not in SECTIONS:
                findings.append(Finding("error", "UNKNOWN_SECTION", number, f"section {name!r} is not one of {', '.join(SECTIONS)}"))
            elif name in section_names:
                findings.append(Finding("warning", "DUPLICATE_SECTION", number, f"section {name} appears twice in one release"))
            section_names.append(name)
    if in_release:
        _check_sections(findings, section_names, current_section_line)

    if unreleased_seen > 1:
        findings.append(Finding("error", "DUPLICATE_UNRELEASED", 1, "more than one [Unreleased] section"))
    if unreleased_seen == 0:
        findings.append(Finding("warning", "NO_UNRELEASED", 1, "no [Unreleased] section for upcoming changes"))

    keys = [_semver_key(v) for _, v in versions]
    for idx in range(1, len(keys)):
        if keys[idx] >= keys[idx - 1]:
            findings.append(Finding("error", "ORDER", versions[idx][0], f"release {versions[idx][1]} should be older than {versions[idx - 1][1]}"))
            break

    link_defs = {m.group("ver") for line in content_lines if (m := LINK_DEF_RE.match(line))}
    for number, ver in versions:
        if ver not in link_defs:
            findings.append(Finding("warning", "NO_LINK", number, f"release {ver} has no link definition at the bottom"))
    return findings


def _check_sections(findings: list[Finding], names: list[str], line: int | None) -> None:
    if line is not None and not names:
        findings.append(Finding("warning", "EMPTY_RELEASE", line, "release has no change sections"))


def lint_file(path: str | Path, today: date | None = None) -> list[Finding]:
    return lint(Path(path).read_text(encoding="utf-8", errors="replace"), today=today)
