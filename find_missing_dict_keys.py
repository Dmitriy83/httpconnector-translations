"""Find Cyrillic identifiers used in RU source that are missing as keys in common-camelcase_en.dict.

These are the identifiers EDT cannot translate → they stay Cyrillic in the translated module.
"""
import re
from pathlib import Path

RU_MOD = Path(r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/HTTP connector/HTTPConnector_ru/src/CommonModules/КоннекторHTTP/Module.bsl")
DICT = Path(r"C:/git/HTTPConnector/dictionaries_en/src/common-camelcase_en.dict")
OUT = Path(r"C:/git/1c-translations-with-model/missing_keys.out")

text = RU_MOD.read_bytes().decode("utf-8-sig")

# Strip out all string literals "..." to avoid picking up literal text
no_str = re.sub(r'"[^"]*"', '""', text)

# Strip line comments starting with //
no_comments = re.sub(r"//[^\n]*", "", no_str)

# Find all identifiers (Russian + Latin CamelCase)
idents = set(re.findall(r"[A-Za-zА-Яа-яЁё_][A-Za-z0-9А-Яа-яЁё_]*", no_comments))

# Only Cyrillic-containing identifiers are what EDT needs to translate
CYR = re.compile(r"[А-Яа-яЁё]")
cyr_idents = {i for i in idents if CYR.search(i)}

# Load dict keys
dict_keys = set()
for ln in DICT.read_bytes().decode("utf-8-sig").splitlines():
    if not ln or ln.startswith("#"):
        continue
    i = 0
    while i < len(ln):
        if ln[i] == "\\" and i + 1 < len(ln):
            i += 2
            continue
        if ln[i] == "=":
            break
        i += 1
    if i < len(ln):
        dict_keys.add(ln[:i])

missing = sorted(cyr_idents - dict_keys)
covered = cyr_idents & dict_keys

with OUT.open("w", encoding="utf-8") as f:
    f.write(f"identifiers in source (Cyrillic only): {len(cyr_idents)}\n")
    f.write(f"covered by camelcase dict: {len(covered)}\n")
    f.write(f"MISSING from camelcase dict: {len(missing)}\n\n")
    f.write("=== Missing identifiers (these stay Russian in translated module) ===\n")
    for m in missing:
        f.write(f"  {m}\n")

print(f"wrote {OUT}")
print(f"cyr idents in source: {len(cyr_idents)}")
print(f"missing from dict: {len(missing)}")
