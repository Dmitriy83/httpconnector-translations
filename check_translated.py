"""Analyze the EDT-translated module for leftover Cyrillic and translation gaps."""
import re
from pathlib import Path

MOD = Path(r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/HTTP connector/HTTPConnector_translated_project/src/CommonModules/ConnectorHTTP/Module.bsl")
OUT = Path(r"C:/git/1c-translations-with-model/check_translated.out")

text = MOD.read_bytes().decode("utf-8-sig")
lines = text.split("\n")

# Find lines with Cyrillic
cyr_lines = [(i, ln) for i, ln in enumerate(lines, 1) if re.search(r"[А-Яа-яЁё]", ln)]

# Find functions
fn_re = re.compile(r"(?:^|\n)\s*(Function|Функция|Procedure|Процедура)\s+([A-Za-z0-9_А-Яа-яЁё]+)")
fns = [(m.start(), m.group(2)) for m in fn_re.finditer(text)]
cyr_fns = [(pos, name) for pos, name in fns if re.search(r"[А-Яа-яЁё]", name)]

# For each Cyrillic function, get line number
def line_of(pos):
    return text[:pos].count("\n") + 1

# Extract individual Cyrillic TOKENS from all lines
tokens = set()
for _, ln in cyr_lines:
    for m in re.finditer(r"[А-Яа-яЁё][А-Яа-яЁё0-9]*", ln):
        tokens.add(m.group(0))

with OUT.open("w", encoding="utf-8") as f:
    f.write(f"total lines: {len(lines)}\n")
    f.write(f"lines with Cyrillic: {len(cyr_lines)}\n")
    f.write(f"functions total: {len(fns)}\n")
    f.write(f"functions with Cyrillic: {len(cyr_fns)}\n\n")

    f.write("=== Cyrillic function names ===\n")
    for pos, name in cyr_fns:
        f.write(f"  line {line_of(pos)}: {name}\n")

    f.write(f"\n=== Unique Cyrillic tokens in module ({len(tokens)}) ===\n")
    for t in sorted(tokens):
        f.write(f"  {t}\n")

    f.write(f"\n=== Cyrillic lines (first 30) ===\n")
    for i, ln in cyr_lines[:30]:
        f.write(f"  {i:5d}: {ln.rstrip()}\n")

print(f"wrote {OUT}")
