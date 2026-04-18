"""Restore string literals in the translated Tests/ObjectModule.bsl from the RU source.

EDT translated Russian string literals into English via the camelcase dict
(e.g., "Секретный ключ" -> "Secret key"). For tests that compare bytes
(HMAC, URL encoding, hash), this changes test semantics and breaks tests.

Strategy: do line-by-line comparison with RU source. For each line where an
English literal differs from the corresponding Russian literal, pick the RU
form — UNLESS the literal is a pure identifier (no whitespace or special
chars) that looks like a procedure name used by Execute().

Run after every EDT rebuild + postbuild_patch.py (or include in patcher).
"""
import re
from pathlib import Path

RU = Path(r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/HTTP connector/HTTPConnector_ru/src/DataProcessors/Тесты/ObjectModule.bsl")
EN = Path(r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/HTTP connector/HTTPConnector_translated_project/src/DataProcessors/Tests/ObjectModule.bsl")

LIT = re.compile(r'"([^"]*)"')
CYR = re.compile(r"[А-Яа-яЁё]")


def is_identifier_like(s: str) -> bool:
    """A literal that's a pure identifier (letters, digits, underscore, optional dots/commas for
    struct key lists like 'Name, Value') — leave translated, since these usually are procedure
    names for Execute() or consistent struct keys."""
    # Reject if contains chars typical of data: space-with-non-comma, hyphen, special chars, equals in middle, exclamation, etc.
    if re.search(r"[ \-!?|%&?=:/<>]", s):
        # But allow "Name, Value" style (comma + single space between identifier tokens)
        # Normalize: remove commas and single spaces, check remaining
        compact = re.sub(r",\s*", "", s)
        if re.match(r"^[A-Za-zА-Яа-яЁё0-9_]+$", compact):
            return True
        return False
    return bool(re.match(r"^[A-Za-zА-Яа-яЁё0-9_]+$", s))


raw_en = EN.read_bytes()
has_bom = raw_en.startswith(b"\xef\xbb\xbf")
body_en = raw_en[3:] if has_bom else raw_en
text_en = body_en.decode("utf-8")
had_crlf = "\r\n" in text_en
if had_crlf:
    text_en = text_en.replace("\r\n", "\n")
en_lines = text_en.split("\n")

ru_text = RU.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
ru_lines = ru_text.split("\n")

reverted = 0
out_lines = []
for i, en_line in enumerate(en_lines):
    if i >= len(ru_lines):
        out_lines.append(en_line)
        continue
    ru_line = ru_lines[i]
    ru_lits = LIT.findall(ru_line)
    en_lits = LIT.findall(en_line)
    if len(ru_lits) != len(en_lits):
        out_lines.append(en_line)
        continue
    new_line = en_line
    for ru_lit, en_lit in zip(ru_lits, en_lits):
        if ru_lit == en_lit:
            continue
        # Only care about literals with Cyrillic in RU version
        if not CYR.search(ru_lit):
            continue
        # Skip identifier-like literals (procedure names / struct keys) — leave translated
        if is_identifier_like(ru_lit):
            continue
        # Revert: replace EN literal with RU literal in this line
        new_line = new_line.replace(f'"{en_lit}"', f'"{ru_lit}"', 1)
        reverted += 1
    out_lines.append(new_line)

out_text = "\n".join(out_lines)
if had_crlf:
    out_text = out_text.replace("\n", "\r\n")
out_raw = out_text.encode("utf-8")
if has_bom:
    out_raw = b"\xef\xbb\xbf" + out_raw
EN.write_bytes(out_raw)

print(f"reverted {reverted} literal(s) in test module")
