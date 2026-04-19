"""Extract untranslated entries from Module_en.trans for the LLM phase.

A "untranslated" entry is one where the key was NOT matched to the old dict
(i.e., the value is still in the source language — Russian).

Outputs:
- glossary.txt: already-translated keys/values (for use as terminology reference)
- untranslated.txt: TSV-like `key<TAB>russian_value` lines to translate
"""
import re
from pathlib import Path

OLD_DICT = Path(r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/HTTP connector/dictionaries_en_old/src/CommonModules/HTTPConnector/Module_ro.trans")
NEW_DICT = Path(r"C:/git/HTTPConnector/dictionaries_en/src/CommonModules/КоннекторHTTP/Module_en.trans")
OUT_DIR = Path(r"C:/git/1c-translations-with-model")


def read_text(p):
    raw = p.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.decode("utf-8")


def split_kv(line):
    i = 0
    while i < len(line):
        if line[i] == "\\" and i + 1 < len(line):
            i += 2
            continue
        if line[i] == "=":
            return line[:i], line[i + 1:]
        i += 1
    return None


def read_props_ordered(p):
    """Return list of (key, value) in file order."""
    out = []
    for ln in read_text(p).splitlines():
        if not ln or ln.startswith("#"):
            continue
        kv = split_kv(ln)
        if kv:
            out.append(kv)
    return out


def has_cyrillic(s):
    return bool(re.search(r"[А-Яа-яЁё]", s))


new_entries = read_props_ordered(NEW_DICT)
old_dict = dict(read_props_ordered(OLD_DICT))

# Currently-translated: value has no Cyrillic (already migrated via phase A or B)
# This also catches identity values (URL=URL) and technical terms.
glossary = []
untranslated = []
for k, v in new_entries:
    if has_cyrillic(v):
        untranslated.append((k, v))
    else:
        glossary.append((k, v))

(OUT_DIR / "glossary.txt").write_text(
    "\n".join(f"{k}\t{v}" for k, v in glossary),
    encoding="utf-8"
)
(OUT_DIR / "untranslated.txt").write_text(
    "\n".join(f"{k}\t{v}" for k, v in untranslated),
    encoding="utf-8"
)

print(f"glossary (already-translated): {len(glossary)}")
print(f"untranslated (Cyrillic-valued): {len(untranslated)}")
print(f"total entries: {len(new_entries)}")
print(f"\nwrote: {OUT_DIR / 'glossary.txt'}")
print(f"wrote: {OUT_DIR / 'untranslated.txt'}")
