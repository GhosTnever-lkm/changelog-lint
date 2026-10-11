"""changelog-lint [FILE] [--strict] [--json]"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .core import lint


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="changelog-lint", description="Validate CHANGELOG.md against Keep a Changelog (offline).")
    p.add_argument("file", nargs="?", default="CHANGELOG.md")
    p.add_argument("--strict", action="store_true", help="warnings fail the run")
    p.add_argument("--json", action="store_true")
    p.add_argument("--version", action="version", version=__version__)
    args = p.parse_args(argv)
    try:
        text = Path(args.file).read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"changelog-lint: {exc.strerror}: {args.file}", file=sys.stderr)
        return 2
    findings = lint(text)
    if args.json:
        print(json.dumps([f.__dict__ for f in findings], indent=2, ensure_ascii=False))
    elif not findings:
        print(f"OK: {args.file} follows Keep a Changelog")
    for f in findings:
        print(f"{args.file}:{f.line}: [{f.level.upper()}] {f.code} {f.message}")
    failed = any(f.level == "error" for f in findings) or (args.strict and bool(findings))
    return 1 if failed else 0
