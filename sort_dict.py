"""Sort common-camelcase_en.dict alphabetically, removing blank lines within entries.

Theory: EDT may be ignoring entries that appear after the first blank line or
out of alphabetical order. Sorting the file should put all entries in the main
sorted section so EDT picks them up.
"""
from pathlib import Path

TARGET = Path(r"C:/git/HTTPConnector/dictionaries_en/src/common-camelcase_en.dict")


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


raw = TARGET.read_bytes()
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
        k, v = kv
        entries[k] = v

# Sort keys. Use locale-independent sort. EDT likely uses Unicode code point order.
sorted_keys = sorted(entries.keys())

out_lines = []
if header:
    out_lines.append(header)
    out_lines.append("")  # blank line after header
for k in sorted_keys:
    out_lines.append(k + "=" + entries[k])

out_text = eol.join(out_lines) + eol  # trailing EOL
out_raw = out_text.encode("utf-8")
if has_bom:
    out_raw = b"\xef\xbb\xbf" + out_raw
TARGET.write_bytes(out_raw)

print(f"sorted {len(sorted_keys)} entries")
print(f"lines in file: {len(out_lines)}")
