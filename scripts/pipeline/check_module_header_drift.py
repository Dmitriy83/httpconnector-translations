"""Detect drift between RU module-header docstring and the frozen English
translation in ``Module_en.trans`` (the ``Description=`` key).

EDT's translation builder treats the module-level docstring as a single prose
blob keyed by ``Description=`` in ``.trans``. The English value is hand-written
once and never auto-refreshed when the RU source changes — so literal facts
inside the comment (copyright year, version number, URLs, emails) silently
drift behind the upstream RU source.

This script extracts literal patterns (year ranges, version strings) from
the current RU module header and from the EN ``Description=`` value and flags
any mismatch.

Idempotent and read-only by default. Exit 1 if drift is detected.

Usage:
    python scripts/check_module_header_drift.py
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

# Pairs of (RU module .bsl, EN .trans) to check. Retarget for other projects.
PAIRS = [
    (
        Path(r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/"
             r"HTTP connector/HTTPConnector_ru/src/CommonModules/КоннекторHTTP/Module.bsl"),
        Path(r"C:/git/httpconnector-translations/dictionaries_en/src/"
             r"CommonModules/КоннекторHTTP/Module_en.trans"),
    ),
]

# Literal patterns to compare. Each entry is (regex, label). The regex must
# capture the whole literal — we use group(0). All occurrences are collected
# from RU and from EN, then compared as ordered lists.
PATTERNS = [
    (re.compile(r"\b[12][0-9]{3}-[12][0-9]{3}\b"),         "year-range"),
    (re.compile(r"\b[0-9]+\.[0-9]+\.[0-9]+\b"),            "version"),
]


def extract_ru_header(bsl: Path) -> str:
    """Return the leading ``// ...`` block from a BSL file (concatenated)."""
    lines = bsl.read_text(encoding="utf-8-sig").splitlines()
    header: list[str] = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("//"):
            header.append(stripped[2:].strip())
        elif stripped == "":
            # blank line inside header — keep going
            header.append("")
        else:
            break
    return "\n".join(header)


def extract_en_description(trans: Path) -> str:
    """Return the value of the top-level ``Description=`` key (un-escaped)."""
    for raw in trans.read_text(encoding="utf-8-sig").splitlines():
        if raw.startswith("Description="):
            value = raw[len("Description="):]
            # Properties-style escapes: \\n -> newline, \\: -> :, \\\\ -> \\
            return (
                value.replace("\\n", "\n")
                     .replace("\\:", ":")
                     .replace("\\\\", "\\")
            )
    return ""


def find_literals(text: str, regex: re.Pattern[str]) -> list[str]:
    return regex.findall(text)


def main() -> int:
    drift_count = 0
    for ru_path, en_path in PAIRS:
        if not ru_path.exists():
            print(f"SKIP: RU file missing: {ru_path}", file=sys.stderr)
            continue
        if not en_path.exists():
            print(f"SKIP: EN .trans missing: {en_path}", file=sys.stderr)
            continue

        ru_text = extract_ru_header(ru_path)
        en_text = extract_en_description(en_path)

        for regex, label in PATTERNS:
            ru_lits = find_literals(ru_text, regex)
            en_lits = find_literals(en_text, regex)
            if ru_lits != en_lits:
                drift_count += 1
                print(f"DRIFT in {ru_path.name} <-> {en_path.name}:")
                print(f"  pattern: {label}")
                print(f"  RU has:  {ru_lits}")
                print(f"  EN has:  {en_lits}")

    if drift_count == 0:
        print("module-header drift: none")
        return 0
    print(f"\n{drift_count} drift(s) detected — update the Description value(s) in the .trans file(s).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
