"""Fix more case issues inherited from old dict migration."""
from pathlib import Path

TARGET = Path(r"C:/git/httpconnector-translations/dictionaries_en/src/common-camelcase_en.dict")

FIXES = {
    "Cookie":   "Cookie",
    "Cookies":  "Cookies",
    "Basic":    "Basic",
    "Digest":   "Digest",
    "Bearer":   "Bearer",
    "Json":     "Json",
    "Client":   "Client",
    "Exceeded": "Exceeded",
    "Length":   "Length",
    "Location": "Location",
    "Other":    "Other",
    "Redirect": "Redirect",
    "URI":      "URI",
    "Version":  "Version",
    "Web":      "Web",
    "SHA256":   "SHA256",   # platform enum HashFunction.SHA256 (not .sha256)
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


raw = TARGET.read_bytes()
has_bom = raw.startswith(b"\xef\xbb\xbf")
if has_bom:
    raw = raw[3:]
text = raw.decode("utf-8")
eol = "\r\n" if "\r\n" in text else "\n"
lines = text.split(eol)

out = []
in_place = 0
# Also scan for suspicious lower-case-value entries
suspicious = []
for ln in lines:
    if not ln or ln.startswith("#"):
        out.append(ln)
        continue
    kv = split_kv(ln)
    if kv is None:
        out.append(ln)
        continue
    k, v = kv
    if k in FIXES and v != FIXES[k]:
        print(f"  fix: {k}: {v} -> {FIXES[k]}")
        out.append(k + "=" + FIXES[k])
        in_place += 1
        continue
    out.append(ln)
    # Flag: PascalCase key → all-lowercase value where key has all upper first letter
    if k and k[0].isupper() and v and v == v.lower() and not any(c.isdigit() for c in v) and len(v) > 2 and v.isascii():
        # identity check — is value == key.lower()?
        if v == k.lower():
            suspicious.append((k, v))

out_text = eol.join(out)
out_raw = out_text.encode("utf-8")
if has_bom:
    out_raw = b"\xef\xbb\xbf" + out_raw
TARGET.write_bytes(out_raw)

print(f"\nfixed: {in_place}")
print(f"\nSuspicious lowercase-valued entries (may break BSL identifier validation):")
for k, v in suspicious[:30]:
    print(f"  {k}={v}")
print(f"  ...({len(suspicious)} total)")
