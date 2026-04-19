"""Tokenize CamelCase identifiers into parts, collect unique Russian tokens.

Tokenization rules:
- Split on lowercase→uppercase boundary, uppercase+lowercase starting at next camel
- Split on letter↔digit, letter↔underscore
- Preserve contiguous Cyrillic or Latin runs
- Keep digits and underscores as separate tokens
"""
import re
from pathlib import Path
from collections import Counter

SRC = Path(r"C:/git/1c-translations-with-model/untr/common-camelcase_en.dict.tsv")


def tokenize(ident):
    """Split an identifier into parts. Returns list of tokens."""
    # insert separators before each uppercase letter that follows lowercase
    # also before digits
    # and around underscores
    tokens = []
    cur = ""

    def flush():
        nonlocal cur
        if cur:
            tokens.append(cur)
            cur = ""

    def char_kind(c):
        if c == "_":
            return "_"
        if c.isdigit():
            return "d"
        if "а" <= c <= "я" or "А" <= c <= "Я" or c in "ёЁ":
            return "c" if c.islower() else "C"  # cyrillic lower/upper
        if c.isalpha():
            return "l" if c.islower() else "L"  # latin lower/upper
        return "x"

    prev = None
    for c in ident:
        k = char_kind(c)
        # Determine if break before current char.
        new_token = False
        if prev is None:
            pass
        elif c == "_" or prev == "_":
            new_token = True
        elif k == "d" and prev != "d":
            new_token = True
        elif prev == "d" and k != "d":
            new_token = True
        elif (prev == "l" and k == "L") or (prev == "c" and k == "C"):
            # lowercase → uppercase
            new_token = True
        elif (prev == "L" and k == "l") or (prev == "C" and k == "c"):
            # uppercase → lowercase: start new token one char back (Mr + P + ain → Mr + Pain)
            if len(cur) > 1:
                tokens.append(cur[:-1])
                cur = cur[-1]
        elif (prev in "lL" and k in "cC") or (prev in "cC" and k in "lL"):
            # latin ↔ cyrillic script boundary
            new_token = True

        if new_token:
            flush()
        cur += c
        prev = k
    flush()
    return tokens


def is_cyrillic(t):
    return bool(re.search(r"[А-Яа-яЁё]", t))


entries = [line.split("\t") for line in SRC.read_text(encoding="utf-8").splitlines() if line]

all_tokens = []
cyr_tokens = Counter()
for k, _v in entries:
    toks = tokenize(k)
    all_tokens.extend(toks)
    for t in toks:
        if is_cyrillic(t):
            cyr_tokens[t] += 1

print(f"entries: {len(entries)}")
print(f"total tokens: {len(all_tokens)}")
print(f"unique cyrillic tokens: {len(cyr_tokens)}")
print(f"\nmost frequent cyrillic tokens (top 100):")
for t, c in cyr_tokens.most_common(100):
    print(f"  {c:>4}  {t}")

# Dump full unique list for translation
OUT = Path(r"C:/git/1c-translations-with-model/camelcase_cyr_tokens.txt")
with OUT.open("w", encoding="utf-8") as f:
    for t, c in cyr_tokens.most_common():
        f.write(f"{t}\t{c}\n")
print(f"\nwrote full list: {OUT}")

# Also dump tokenization sample for verification
print("\nSample tokenization:")
for k, _v in entries[:20]:
    print(f"  {k!r} -> {tokenize(k)}")
