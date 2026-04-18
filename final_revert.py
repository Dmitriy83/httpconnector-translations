"""Revert: move stuck 3 back to common-camelcase (where they were CamelCase)
and leave Имя in common. Then user does full clean+rebuild."""
from pathlib import Path

CAMEL = Path(r"C:/git/HTTPConnector/dictionaries_en/src/common-camelcase_en.dict")
COMMON = Path(r"C:/git/HTTPConnector/dictionaries_en/src/common_en.dict")

BACK_TO_CAMEL = {
    "ПрочитатьZip":           "ReadZip",
    "НоваяCookie":            "NewCookie",
    "ОбработчикиКомандФормы": "FormCommandsEventHandlers",
}


def split_kv(line):
    i = 0
    while i < len(line):
        if line[i] == "\\" and i + 1 < len(line):
            i += 2; continue
        if line[i] == "=":
            return line[:i], line[i + 1:]
        i += 1
    return None


def read_sorted(path):
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    if has_bom: raw = raw[3:]
    text = raw.decode("utf-8")
    eol = "\r\n" if "\r\n" in text else "\n"
    header = None; entries = {}
    for ln in text.split(eol):
        if not ln: continue
        if ln.startswith("#"):
            if header is None: header = ln
            continue
        kv = split_kv(ln)
        if kv: entries[kv[0]] = kv[1]
    return header, entries, eol, has_bom


def write_sorted(path, header, entries, eol, has_bom):
    out_lines = [header, ""] if header else []
    for k in sorted(entries):
        out_lines.append(k + "=" + entries[k])
    out_raw = (eol.join(out_lines) + eol).encode("utf-8")
    if has_bom: out_raw = b"\xef\xbb\xbf" + out_raw
    path.write_bytes(out_raw)


ch, ce, cl, cb = read_sorted(CAMEL)
nh, ne, nl, nb = read_sorted(COMMON)

for k, v in BACK_TO_CAMEL.items():
    if k in ne: del ne[k]
    ce[k] = v

write_sorted(CAMEL, ch, ce, cl, cb)
write_sorted(COMMON, nh, ne, nl, nb)

print(f"camelcase: {len(ce)}")
print(f"common:    {len(ne)}: {sorted(ne)}")
