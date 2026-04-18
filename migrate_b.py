"""Phase B migration for HTTPConnector Module_en.trans.

Strategy:
1. Parse en and ru `Module.bsl` — extract function signatures (name + ordered params).
2. For functions with IDENTICAL names in both (the 18 common ones), zip params positionally
   → build alias map: ru_param → en_param.
3. For each unmatched key in new dict, translate Cyrillic identifiers via alias.
   If the translated key exists in the old dict AND every Cyrillic token resolved — migrate.
4. Write back preserving file structure (header, blank lines, EOL, BOM).
"""
import re
from pathlib import Path

EN_SRC   = Path(r"C:/git/HTTPConnector/src/en/CommonModules/HTTPConnector/Ext/Module.bsl")
RU_SRC   = Path(r"C:/git/HTTPConnector/src/ru/CommonModules/КоннекторHTTP/Ext/Module.bsl")
OLD_DICT = Path(r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/HTTP connector/dictionaries_en_old/src/CommonModules/HTTPConnector/Module_ro.trans")
NEW_DICT = Path(r"C:/git/HTTPConnector/dictionaries_en/src/CommonModules/КоннекторHTTP/Module_en.trans")

APPLY = True  # set False for dry-run


def read_text(p):
    raw = p.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.decode("utf-8")


FN_RE = re.compile(
    r"^\s*(Function|Функция|Procedure|Процедура)\s+([A-Za-z0-9_А-Яа-яЁё]+)\s*\((.*?)\)",
    re.MULTILINE | re.IGNORECASE | re.DOTALL,
)


def extract_functions(src):
    out = []
    for m in FN_RE.finditer(src):
        name = m.group(2)
        params = []
        for p in m.group(3).split(","):
            p = p.strip().split("=", 1)[0].strip()
            toks = p.split()
            if toks and toks[0].lower() in ("val", "знач"):
                toks = toks[1:]
            if toks:
                params.append(toks[0])
        out.append((name, params))
    return out


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


def read_props(p):
    d = {}
    for ln in read_text(p).splitlines():
        if not ln or ln.startswith("#"):
            continue
        kv = split_kv(ln)
        if kv:
            d[kv[0]] = kv[1]
    return d


# --- Build alias map ---
en = extract_functions(read_text(EN_SRC))
ru = extract_functions(read_text(RU_SRC))
en_by = {n: p for n, p in en}
ru_by = {n: p for n, p in ru}

alias = {}
conflicts = {}
common = set(en_by) & set(ru_by)
for name in common:
    ep, rp = en_by[name], ru_by[name]
    if len(ep) != len(rp):
        continue
    for e, r in zip(ep, rp):
        if r == e:
            continue
        existing = alias.get(r)
        if existing and existing != e:
            conflicts.setdefault(r, set()).add(e)
            conflicts[r].add(existing)
        else:
            alias[r] = e

print(f"common funcs: {len(common)}")
print(f"alias pairs:  {len(alias)}")
if conflicts:
    print(f"conflicts: {len(conflicts)}")
    for r, es in list(conflicts.items())[:10]:
        print(f"  {r} -> {sorted(es)}")
print("sample aliases:")
for r, e in list(alias.items())[:20]:
    print(f"  {r} -> {e}")


# --- Find migration candidates ---
IDENT = re.compile(r"[A-Za-z0-9_А-Яа-яЁё]+")


def translate_key(key):
    misses = []
    changed = [False]

    def repl(m):
        t = m.group(0)
        if re.search(r"[А-Яа-яЁё]", t):
            if t in alias:
                changed[0] = True
                return alias[t]
            misses.append(t)
            return t
        return t
    out = IDENT.sub(repl, key)
    return out, misses, changed[0]


old_d = read_props(OLD_DICT)
new_d = read_props(NEW_DICT)
matched = set(old_d) & set(new_d)
unmatched = sorted(set(new_d) - set(old_d))

migrations = {}  # new_key -> value from old dict
for k in unmatched:
    tr, misses, changed = translate_key(k)
    if misses:
        continue  # has unresolved Cyrillic → skip
    if not changed:
        continue  # no Cyrillic at all (shouldn't happen for unmatched, but safe)
    if tr in old_d:
        migrations[k] = old_d[tr]

print(f"\nunmatched keys: {len(unmatched)}")
print(f"migration candidates (phase B): {len(migrations)}")
for k, v in list(migrations.items())[:15]:
    tr, _, _ = translate_key(k)
    print(f"  NEW: {k}")
    print(f"  EN : {tr}")
    print(f"  VAL: {v[:80]}{'…' if len(v) > 80 else ''}")
    print()


# --- Apply migrations ---
if not APPLY:
    print("DRY RUN (APPLY=False): not writing.")
    raise SystemExit(0)

raw = NEW_DICT.read_bytes()
has_bom = raw.startswith(b"\xef\xbb\xbf")
if has_bom:
    raw = raw[3:]
text = raw.decode("utf-8")
eol = "\r\n" if "\r\n" in text else "\n"
lines = text.split(eol)

replaced = 0
out_lines = []
for ln in lines:
    if not ln or ln.startswith("#"):
        out_lines.append(ln)
        continue
    kv = split_kv(ln)
    if kv is None:
        out_lines.append(ln)
        continue
    k, _ = kv
    if k in migrations:
        out_lines.append(k + "=" + migrations[k])
        replaced += 1
    else:
        out_lines.append(ln)

out_text = eol.join(out_lines)
out_raw = out_text.encode("utf-8")
if has_bom:
    out_raw = b"\xef\xbb\xbf" + out_raw
NEW_DICT.write_bytes(out_raw)

print(f"\nwritten: {replaced} replacements in {NEW_DICT}")
