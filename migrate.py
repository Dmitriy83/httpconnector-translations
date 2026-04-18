"""Migrate translation values from old dictionary to new dictionary by exact key match.

For each matching key, replaces the value in the new file with the value from the old file.
Preserves file structure: header, blank lines, line order, line endings, BOM.
"""
from pathlib import Path

OLD_ROOT = Path(r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/HTTP connector/dictionaries_en_old/src")
NEW_ROOT = Path(r"C:/git/HTTPConnector/dictionaries_en/src")

# (old relative path, new relative path)
PAIRS = [
    ("common_ro.dict",                                    "common_en.dict"),
    ("common-camelcase_ro.dict",                          "common-camelcase_en.dict"),
    ("Configuration/Configuration_ro.lstr",               "Configuration/Configuration_en.lstr"),
    ("Configuration/Configuration_ro.trans",              "Configuration/Configuration_en.trans"),
    ("CommonModules/HTTPConnector/HTTPConnector_ro.lstr", "CommonModules/КоннекторHTTP/КоннекторHTTP_en.lstr"),
    ("CommonModules/HTTPConnector/Module_ro.lstr",        "CommonModules/КоннекторHTTP/Module_en.lstr"),
    ("CommonModules/HTTPConnector/Module_ro.trans",       "CommonModules/КоннекторHTTP/Module_en.trans"),
    ("DataProcessors/Tests/Forms/Form/Form_ro.lstr",      "DataProcessors/Тесты/Forms/Форма/Form_en.lstr"),
    ("DataProcessors/Tests/ObjectModule_ro.trans",        "DataProcessors/Тесты/ObjectModule_en.trans"),
    ("DataProcessors/Tests/Tests_ro.lstr",                "DataProcessors/Тесты/Тесты_en.lstr"),
]


def split_kv(line: str):
    """Split a properties line into (key, value). Return None if not a kv line.

    Handles escape sequences \\=, \\:, \\<space> in keys.
    """
    i = 0
    while i < len(line):
        if line[i] == "\\" and i + 1 < len(line):
            i += 2
            continue
        if line[i] == "=":
            return line[:i], line[i + 1:]
        i += 1
    return None


def read_props_dict(path: Path) -> dict:
    d = {}
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    for ln in raw.decode("utf-8").splitlines():
        if not ln or ln.startswith("#"):
            continue
        kv = split_kv(ln)
        if kv:
            d[kv[0]] = kv[1]
    return d


def migrate_file(old_path: Path, new_path: Path):
    old_dict = read_props_dict(old_path)

    raw = new_path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    if has_bom:
        raw = raw[3:]
    text = raw.decode("utf-8")
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(eol)

    replaced = 0
    total_kv = 0
    out = []
    for ln in lines:
        if not ln or ln.startswith("#"):
            out.append(ln)
            continue
        kv = split_kv(ln)
        if kv is None:
            out.append(ln)
            continue
        total_kv += 1
        k, _v = kv
        if k in old_dict:
            out.append(k + "=" + old_dict[k])
            replaced += 1
        else:
            out.append(ln)

    out_text = eol.join(out)
    out_raw = out_text.encode("utf-8")
    if has_bom:
        out_raw = b"\xef\xbb\xbf" + out_raw
    new_path.write_bytes(out_raw)
    return replaced, total_kv


def main():
    print(f"{'file':<60} {'replaced':>10} {'total':>7} {'%':>6}")
    grand_replaced = grand_total = 0
    for old_rel, new_rel in PAIRS:
        old_p = OLD_ROOT / old_rel
        new_p = NEW_ROOT / new_rel
        if not old_p.exists():
            print(f"SKIP (old missing): {old_rel}")
            continue
        if not new_p.exists():
            print(f"SKIP (new missing): {new_rel}")
            continue
        r, t = migrate_file(old_p, new_p)
        grand_replaced += r
        grand_total += t
        pct = (100 * r / t) if t else 0
        print(f"{new_rel:<60} {r:>10} {t:>7} {pct:>5.1f}%")
    pct = (100 * grand_replaced / grand_total) if grand_total else 0
    print(f"\nTOTAL replaced: {grand_replaced} / {grand_total}  ({pct:.1f}%)")


if __name__ == "__main__":
    main()
