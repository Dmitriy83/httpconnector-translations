"""Estimate coverage for approaches B (alias map → old dict) and C (alias map → en src doc comments).

Approach B:  ru key → (alias_map) → en key → lookup in OLD dict
Approach C:  ru key → (alias_map) → en key → lookup in en src doc comments (parsed from Module.bsl)
"""
import re
from pathlib import Path

EN_SRC = Path(r"C:/git/HTTPConnector/src/en/CommonModules/HTTPConnector/Ext/Module.bsl")
RU_SRC = Path(r"C:/git/HTTPConnector/src/ru/CommonModules/КоннекторHTTP/Ext/Module.bsl")
OLD_DICT = Path(r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/HTTP connector/dictionaries_en_old/src/CommonModules/HTTPConnector/Module_ro.trans")
NEW_DICT = Path(r"C:/git/httpconnector-translations/dictionaries_en/src/CommonModules/КоннекторHTTP/Module_en.trans")


def read_text(p):
    raw = p.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.decode("utf-8")


def read_props(p):
    d = {}
    for ln in read_text(p).splitlines():
        if not ln or ln.startswith("#"):
            continue
        i = 0
        while i < len(ln):
            if ln[i] == "\\" and i + 1 < len(ln):
                i += 2
                continue
            if ln[i] == "=":
                break
            i += 1
        if i < len(ln):
            d[ln[:i]] = ln[i + 1:]
    return d


# --- BSL parser: extract function name + ordered list of parameter names ---
# Supports both "Function Name(...)" (en) and "Функция Name(...)" (ru).
FN_RE = re.compile(r"(?:^|\n)\s*(?:Function|Функция|Procedure|Процедура)\s+([A-Za-z0-9_А-Яа-яЁё]+)\s*\((.*?)\)",
                   re.IGNORECASE | re.DOTALL)


def extract_functions(src_text):
    """Return list of (func_name, [param_names]) in order of appearance."""
    out = []
    for m in FN_RE.finditer(src_text):
        name = m.group(1)
        raw_params = m.group(2)
        # strip default values and keyword 'Val'/'Знач'
        params = []
        for p in raw_params.split(","):
            p = p.strip()
            if not p:
                continue
            # drop default
            p = p.split("=", 1)[0].strip()
            # drop Val/Знач prefix
            toks = p.split()
            if toks and toks[0].lower() in ("val", "знач"):
                toks = toks[1:]
            if toks:
                params.append(toks[0])
        out.append((name, params))
    return out


en_text = read_text(EN_SRC)
ru_text = read_text(RU_SRC)

en_funcs = extract_functions(en_text)
ru_funcs = extract_functions(ru_text)

print(f"en functions: {len(en_funcs)}  ru functions: {len(ru_funcs)}")

# Pair functions by name (function names are mostly preserved — same English-like names in both versions).
en_by_name = {n: p for n, p in en_funcs}
ru_by_name = {n: p for n, p in ru_funcs}

common_names = set(en_by_name) & set(ru_by_name)
only_en = set(en_by_name) - set(ru_by_name)
only_ru = set(ru_by_name) - set(en_by_name)
print(f"functions paired by exact name: {len(common_names)}")
print(f"only in en: {len(only_en)}   only in ru: {len(only_ru)}")
if only_en:
    print(f"  en-only sample: {list(only_en)[:10]}")
if only_ru:
    print(f"  ru-only sample: {list(only_ru)[:10]}")

# Build param alias map: ru_param -> en_param (positional zip per common function)
alias = {}
alias_conflicts = {}
for name in common_names:
    ens = en_by_name[name]
    rus = ru_by_name[name]
    if len(ens) != len(rus):
        # skip if arity differs — risky to align
        continue
    for en_p, ru_p in zip(ens, rus):
        if ru_p == en_p:
            continue  # trivial identity (URL=URL etc.)
        existing = alias.get(ru_p)
        if existing and existing != en_p:
            alias_conflicts.setdefault(ru_p, set()).add(en_p)
            alias_conflicts[ru_p].add(existing)
        else:
            alias[ru_p] = en_p

print(f"\nru->en param aliases: {len(alias)} (unique)")
print(f"ambiguous aliases (different en for same ru): {len(alias_conflicts)}")
print("sample aliases:")
for ru_p, en_p in list(alias.items())[:20]:
    print(f"  {ru_p} -> {en_p}")

# Also add identity for function names (Get->Get etc.)
# And for params that are identical (URL stays URL).

# --- Rebuild new dict unmatched-keys and try to resolve via alias ---
old_dict = read_props(OLD_DICT)
new_dict = read_props(NEW_DICT)
matched = set(old_dict) & set(new_dict)
unmatched = sorted(set(new_dict) - set(old_dict))

print(f"\nModule.trans: new_keys={len(new_dict)} matched={len(matched)} unmatched={len(unmatched)}")

# For each unmatched key, try to translate ru identifiers to en and look up in old dict.
IDENT_RE = re.compile(r"[A-Za-z0-9_А-Яа-яЁё]+")

def translate_key_ru_to_en(key):
    # Split key into tokens separated by "." (but keep escape-sequences inside tokens).
    # Easy approach: replace every Cyrillic-containing identifier via alias.
    def repl(m):
        tok = m.group(0)
        # if contains Cyrillic, try alias
        if re.search(r"[А-Яа-яЁё]", tok):
            if tok in alias:
                return alias[tok]
            # Cyrillic but no alias — signal unknown
            return "<?>" + tok
        return tok
    return IDENT_RE.sub(repl, key)


resolved_B = 0   # translated key exists in old dict
resolved_unknown = 0  # contained Cyrillic token without alias
no_cyrillic = 0  # unmatched but no Cyrillic — probably structural (NStr escape etc.)
examples_B = []
examples_unknown = []
for k in unmatched:
    tr = translate_key_ru_to_en(k)
    if "<?>" in tr:
        resolved_unknown += 1
        if len(examples_unknown) < 10:
            examples_unknown.append((k, tr))
        continue
    if not re.search(r"[А-Яа-яЁё]", k):
        no_cyrillic += 1
        continue
    if tr in old_dict:
        resolved_B += 1
        if len(examples_B) < 10:
            examples_B.append((k, tr, old_dict[tr]))

print(f"\nApproach B estimate (alias -> old dict lookup):")
print(f"  unmatched without Cyrillic (structural, won't be helped): {no_cyrillic}")
print(f"  contain unresolvable Cyrillic token (no alias): {resolved_unknown}")
print(f"  resolved via alias and FOUND in old dict: {resolved_B}")

print(f"\nExample resolved (B):")
for k, tr, v in examples_B:
    print(f"  NEW  {k}")
    print(f"  OLD  {tr}")
    print(f"  VAL  {v[:80]}{'…' if len(v)>80 else ''}")
    print()

print(f"\nExample unresolved (unknown Cyrillic tokens):")
for k, tr in examples_unknown[:10]:
    print(f"  NEW  {k}")
    print(f"  TR   {tr}")
    # Extract unresolved tokens
    unresolved_tokens = re.findall(r"<\?>[А-Яа-яЁё_]+", tr)
    print(f"  MISS {unresolved_tokens}")
    print()
