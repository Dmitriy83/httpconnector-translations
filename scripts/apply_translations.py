"""Apply translations from translations_module_trans.py to Module_en.trans.

Reads the target file line-by-line, for any line whose key exists in TR,
replaces the value. Preserves file structure (header, blank lines, EOL, BOM).
"""
from pathlib import Path
import importlib.util

TARGET = Path(r"C:/git/httpconnector-translations/dictionaries_en/src/CommonModules/КоннекторHTTP/Module_en.trans")
SRC = Path(r"C:/git/1c-translations-with-model/scripts/translations_module_trans.py")


def load_tr():
    spec = importlib.util.spec_from_file_location("tr_mod", SRC)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.TR


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


def main():
    TR = load_tr()
    print(f"translations loaded: {len(TR)}")

    raw = TARGET.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    if has_bom:
        raw = raw[3:]
    text = raw.decode("utf-8")
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(eol)

    # Collect existing keys for audit
    file_keys = set()
    for ln in lines:
        if not ln or ln.startswith("#"):
            continue
        kv = split_kv(ln)
        if kv:
            file_keys.add(kv[0])

    missing_in_file = set(TR) - file_keys
    missing_in_tr = set()  # keys with Russian value in file but not in TR — we'll detect those later

    print(f"keys in file: {len(file_keys)}")
    print(f"keys in TR not found in file: {len(missing_in_file)}")
    for k in sorted(missing_in_file)[:10]:
        print(f"  MISSING: {k}")

    replaced = 0
    out = []
    for ln in lines:
        if not ln or ln.startswith("#"):
            out.append(ln)
            continue
        kv = split_kv(ln)
        if kv is None:
            out.append(ln)
            continue
        k, _ = kv
        if k in TR:
            out.append(k + "=" + TR[k])
            replaced += 1
        else:
            out.append(ln)

    out_text = eol.join(out)
    out_raw = out_text.encode("utf-8")
    if has_bom:
        out_raw = b"\xef\xbb\xbf" + out_raw
    TARGET.write_bytes(out_raw)

    print(f"\nreplaced: {replaced}")


if __name__ == "__main__":
    main()
