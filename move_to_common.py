"""Move non-CamelCase-looking entries from common-camelcase_en.dict to common_en.dict.

Hypothesis: EDT's translation storage order classifies identifiers as CamelCase
or non-CamelCase. Entries that don't match CamelCase heuristic (single Cyrillic
word, or mixed Cyrillic+Latin) are looked up in 'Model common non-CamelCase
translations' storage = common_en.dict, not in common-camelcase_en.dict.
"""
from pathlib import Path

CAMEL = Path(r"C:/git/HTTPConnector/dictionaries_en/src/common-camelcase_en.dict")
COMMON = Path(r"C:/git/HTTPConnector/dictionaries_en/src/common_en.dict")

# Identifiers that EDT has NOT been translating from camelcase dict
TO_MOVE = {
    "Имя":                    "Name",
    "НоваяCookie":            "NewCookie",
    "ПрочитатьZip":           "ReadZip",
    "ОбработчикиКомандФормы": "FormCommandsEventHandlers",
}


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


def read_sorted_entries(path):
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    if has_bom:
        raw = raw[3:]
    text = raw.decode("utf-8")
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(eol)
    header = None
    entries = {}
    for ln in lines:
        if not ln:
            continue
        if ln.startswith("#"):
            if header is None:
                header = ln
            continue
        kv = split_kv(ln)
        if kv:
            entries[kv[0]] = kv[1]
    return header, entries, eol, has_bom


def write_sorted(path, header, entries, eol, has_bom):
    out_lines = []
    if header:
        out_lines.append(header)
        out_lines.append("")
    for k in sorted(entries):
        out_lines.append(k + "=" + entries[k])
    out_text = eol.join(out_lines) + eol
    out_raw = out_text.encode("utf-8")
    if has_bom:
        out_raw = b"\xef\xbb\xbf" + out_raw
    path.write_bytes(out_raw)


# Load both
cheader, centries, ceol, cbom = read_sorted_entries(CAMEL)
nheader, nentries, neol, nbom = read_sorted_entries(COMMON)

print(f"camelcase: {len(centries)} entries")
print(f"common:    {len(nentries)} entries")

# Remove from camelcase, add to common
removed = 0
added = 0
for k, v in TO_MOVE.items():
    if k in centries:
        del centries[k]
        removed += 1
    if k not in nentries:
        nentries[k] = v
        added += 1
    else:
        nentries[k] = v  # update in case value differs

# Use common's eol/bom for output
write_sorted(CAMEL, cheader, centries, ceol, cbom)
write_sorted(COMMON, nheader, nentries, neol or "\r\n", nbom)

print(f"\nremoved from camelcase: {removed}")
print(f"added/updated in common: {added}")
print(f"common now has {len(nentries)} entries")

print(f"\ncommon_en.dict contents:")
for k in sorted(nentries):
    print(f"  {k}={nentries[k]}")
