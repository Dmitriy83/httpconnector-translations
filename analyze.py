import re
from pathlib import Path

OLD = Path(r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/HTTP connector/dictionaries_en_old/src")
NEW = Path(r"C:/git/HTTPConnector/dictionaries_en/src")

def read_props(p):
    d = {}
    for ln in p.read_text(encoding="utf-8").splitlines():
        if ln.startswith("#") or not ln.strip():
            continue
        i = 0
        while i < len(ln):
            if ln[i] == '\\':
                i += 2; continue
            if ln[i] == '=':
                break
            i += 1
        if i < len(ln):
            d[ln[:i]] = ln[i+1:]
    return d

pairs = [
    ("CommonModules/HTTPConnector/Module_ro.trans", "CommonModules/КоннекторHTTP/Module_en.trans", "Module.trans"),
    ("Configuration/Configuration_ro.lstr",         "Configuration/Configuration_en.lstr",         "Configuration.lstr"),
    ("Configuration/Configuration_ro.trans",        "Configuration/Configuration_en.trans",        "Configuration.trans"),
    ("common_ro.dict",                              "common_en.dict",                              "common.dict"),
    ("common-camelcase_ro.dict",                    "common-camelcase_en.dict",                    "common-camelcase.dict"),
]

for rel_old, rel_new, label in pairs:
    o = read_props(OLD / rel_old)
    n = read_props(NEW / rel_new)
    inter = sorted(set(o) & set(n))
    print(f"\n=== {label}: {len(inter)} matching keys ===")
    # Show up to 10 examples: key, old_value, new_value
    for k in inter[:10]:
        ov = o[k][:80] + ("…" if len(o[k]) > 80 else "")
        nv = n[k][:80] + ("…" if len(n[k]) > 80 else "")
        print(f"  KEY:      {k}")
        print(f"  old(EN):  {ov}")
        print(f"  new(RU):  {nv}")
        print()

    # Also show 5 keys in new NOT in old (to see what's unique)
    diff = sorted(set(n) - set(o))
    print(f"  [--- {len(diff)} keys in new NOT in old, first 5: ---]")
    for k in diff[:5]:
        nv = n[k][:80] + ("…" if len(n[k]) > 80 else "")
        print(f"  KEY:      {k}")
        print(f"  new(RU):  {nv}")
        print()
