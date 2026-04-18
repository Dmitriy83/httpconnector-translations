"""Find string literals in the translated test module that LIKELY got mistranslated by EDT.

Compares each string literal between RU source and translated output by LINE.
Reports literals whose content differs when they should be byte-equivalent test data.
"""
import re
from pathlib import Path

RU = Path(r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/HTTP connector/HTTPConnector_ru/src/DataProcessors/Тесты/ObjectModule.bsl")
EN = Path(r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/HTTP connector/HTTPConnector_translated_project/src/DataProcessors/Tests/ObjectModule.bsl")

ru_lines = RU.read_text(encoding="utf-8-sig").split("\n")
en_lines = EN.read_text(encoding="utf-8-sig").split("\n")

# Line count should match (1:1 translation)
print(f"RU lines: {len(ru_lines)}, EN lines: {len(en_lines)}")

LIT = re.compile(r'"([^"]*)"')

CYR = re.compile(r"[А-Яа-яЁё]")

mismatches = []
min_lines = min(len(ru_lines), len(en_lines))
for i in range(min_lines):
    ru_lits = LIT.findall(ru_lines[i])
    en_lits = LIT.findall(en_lines[i])
    if len(ru_lits) != len(en_lits):
        continue
    for ru_lit, en_lit in zip(ru_lits, en_lits):
        if ru_lit == en_lit:
            continue
        # Only report when RU literal has Cyrillic (= literal got translated)
        if CYR.search(ru_lit):
            mismatches.append((i + 1, ru_lit, en_lit))

out = Path(r"C:/git/1c-translations-with-model/mistranslated_literals.out")
with out.open("w", encoding="utf-8") as f:
    f.write(f"Found {len(mismatches)} string literals with Cyrillic in RU that got translated:\n\n")
    for lineno, ru_lit, en_lit in mismatches:
        f.write(f"line {lineno}:\n")
        f.write(f"  RU: {ru_lit!r}\n")
        f.write(f"  EN: {en_lit!r}\n\n")

print(f"wrote {out}, {len(mismatches)} mismatches")
