"""Undo previously-added override for СтрЗаканчиваетсяНа and revert
translated module's StrEndWith( back to StrEndsWith( (EDT default is correct)."""
from pathlib import Path

CAMEL = Path(r"C:/git/HTTPConnector/dictionaries_en/src/common-camelcase_en.dict")
TRANSLATED = Path(r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/HTTP connector/HTTPConnector_translated_project/src/CommonModules/ConnectorHTTP/Module.bsl")


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


# --- remove СтрЗаканчиваетсяНа override from dict ---
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

if "СтрЗаканчиваетсяНа" in entries:
    del entries["СтрЗаканчиваетсяНа"]
    print("removed: СтрЗаканчиваетсяНа override from dict")

out_lines = [header, ""] if header else []
for k in sorted(entries):
    out_lines.append(k + "=" + entries[k])
out_raw = (eol.join(out_lines) + eol).encode("utf-8")
if has_bom:
    out_raw = b"\xef\xbb\xbf" + out_raw
CAMEL.write_bytes(out_raw)

# --- revert StrEndWith( in translated module ---
raw = TRANSLATED.read_bytes()
has_bom = raw.startswith(b"\xef\xbb\xbf")
body = raw[3:] if has_bom else raw
text = body.decode("utf-8")
had_crlf = "\r\n" in text

n = text.count("StrEndWith(")
text = text.replace("StrEndWith(", "StrEndsWith(")
print(f"reverted: {n} StrEndWith( -> StrEndsWith(")

new_raw = text.encode("utf-8")
if has_bom:
    new_raw = b"\xef\xbb\xbf" + new_raw
TRANSLATED.write_bytes(new_raw)
