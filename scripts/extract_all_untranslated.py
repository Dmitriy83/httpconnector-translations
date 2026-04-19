"""Extract untranslated entries from ALL HTTPConnector dict files.

For each file: only keys whose value still contains Cyrillic are considered untranslated.
Outputs per-file files under `untr/` for manual translation.
"""
import re
from pathlib import Path

NEW_ROOT = Path(r"C:/git/httpconnector-translations/dictionaries_en/src")
OUT_DIR = Path(r"C:/git/1c-translations-with-model/untr")
OUT_DIR.mkdir(exist_ok=True)

FILES = [
    "common_en.dict",
    "common-camelcase_en.dict",
    "Configuration/Configuration_en.lstr",
    "Configuration/Configuration_en.trans",
    "CommonModules/КоннекторHTTP/КоннекторHTTP_en.lstr",
    "CommonModules/КоннекторHTTP/Module_en.lstr",
    "CommonModules/КоннекторHTTP/Module_en.trans",
    "DataProcessors/Тесты/Forms/Форма/Form_en.lstr",
    "DataProcessors/Тесты/ObjectModule_en.trans",
    "DataProcessors/Тесты/Тесты_en.lstr",
]


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


def read_entries(p):
    out = []
    for ln in read_text(p).splitlines():
        if not ln or ln.startswith("#"):
            continue
        kv = split_kv(ln)
        if kv:
            out.append(kv)
    return out


CYR = re.compile(r"[А-Яа-яЁё]")

totals = []
for rel in FILES:
    p = NEW_ROOT / rel
    entries = read_entries(p)
    untr = [(k, v) for k, v in entries if CYR.search(v)]
    totals.append((rel, len(entries), len(untr)))
    # write per-file untr
    safe_name = rel.replace("/", "__").replace("\\", "__")
    (OUT_DIR / f"{safe_name}.tsv").write_text(
        "\n".join(f"{k}\t{v}" for k, v in untr),
        encoding="utf-8"
    )

print(f"{'file':<60} {'total':>6} {'untr':>6}")
grand_total = grand_untr = 0
for rel, t, u in totals:
    print(f"{rel:<60} {t:>6} {u:>6}")
    grand_total += t
    grand_untr += u
print(f"\nGRAND TOTAL: total={grand_total}  untranslated={grand_untr}")
