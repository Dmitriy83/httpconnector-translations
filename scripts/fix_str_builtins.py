"""Override EDT's platform-dictionary translations of СтрНачинаетсяС/СтрЗаканчиваетсяНа.

EDT maps them to StrStartsWith/StrEndsWith — but the actual 1C platform
English aliases are StrStartWith/StrEndWith (no "s" in Start/End).

By adding these entries to common-camelcase_en.dict (user dict), EDT's
user storage (higher priority than platform context) overrides the
platform default.
"""
from pathlib import Path

CAMEL = Path(r"C:/git/HTTPConnector/dictionaries_en/src/common-camelcase_en.dict")

OVERRIDES = {
    # Only StrStartsWith is wrong in EDT's platform dictionary.
    # StrEndsWith is correct as-is (EDT already maps to that).
    "СтрНачинаетсяС": "StrStartWith",
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


raw = CAMEL.read_bytes()
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

for k, v in OVERRIDES.items():
    entries[k] = v
    print(f"set: {k}={v}")

out_lines = [header, ""] if header else []
for k in sorted(entries):
    out_lines.append(k + "=" + entries[k])
out_text = eol.join(out_lines) + eol
out_raw = out_text.encode("utf-8")
if has_bom:
    out_raw = b"\xef\xbb\xbf" + out_raw
CAMEL.write_bytes(out_raw)

print(f"\ntotal: {len(entries)} entries")
