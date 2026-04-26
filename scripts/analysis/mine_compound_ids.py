"""Mine compound-identifier RU->EN mappings from the old hand-translated source.

Inputs:
- RU module (working tree, unchanged from commit) from C:/git/HTTPConnector/src/ru/...
- OLD EN module — committed version, via `git show HEAD:src/en/...` — this is the
  hand-translated English source we want to emulate.

For each line pair (same line number), extract Cyrillic identifiers from RU and
Latin identifiers from EN. Each Cyrillic identifier becomes a key; the
corresponding Latin identifier at the same positional index within the line is
the proposed value.

Filter: only keep COMPOUND identifiers (>=2 capitalized word parts in RU), since
single-word tokens (Запрос, Ответ, Данные) are already handled by the camelcase
dict's word-level entries.

Output: write a sorted, de-duplicated list of `RU=EN` suggestions to
stdout, grouped by confidence. Confidence is based on consistency — if the
same RU identifier maps to the same EN identifier across multiple lines,
confidence is HIGH; if it maps to different ENs, we list all and mark LOW.
"""
from __future__ import annotations
import difflib
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(r"C:/git/HTTPConnector")

PAIRS = [
    # (ru_path_relative, en_path_relative) — same path shape, language swap
    ("src/ru/CommonModules/КоннекторHTTP/Ext/Module.bsl",
     "src/en/CommonModules/HTTPConnector/Ext/Module.bsl"),
    ("src/ru/DataProcessors/Тесты/Ext/ObjectModule.bsl",
     "src/en/DataProcessors/Tests/Ext/ObjectModule.bsl"),
    ("src/ru/DataProcessors/Тесты/Forms/Форма/Ext/Form/Module.bsl",
     "src/en/DataProcessors/Tests/Forms/Form/Ext/Form/Module.bsl"),
]

# An identifier token: starts with a letter/underscore, then letters/digits/underscores.
# We accept mixed Cyrillic+Latin (e.g. "СоставURL", "НоваяCookie").
ID_RE = re.compile(r"[A-Za-zА-Яа-яЁё_][A-Za-zА-Яа-яЁё0-9_]*")
CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")

# Capital-word counter for a token: count runs of Uppercase+lowercase.
# Examples: "СписокТестов" -> 2, "РаботаССессиями" -> 3 (Работа, С, Сессиями),
# "Cookies" -> 1, "URLComposition" -> 2 (URL, Composition).
WORD_RE = re.compile(r"[A-ZА-ЯЁ][a-zа-яё0-9]*|[A-Z]+(?![a-zа-яё])|[А-ЯЁ]+(?![а-яё])")


def read_old_en(rel: str) -> str:
    """Read the committed version of an EN file (not the working tree)."""
    out = subprocess.check_output(
        ["git", "-C", str(REPO), "show", f"HEAD:{rel}"],
        encoding="utf-8-sig",
    )
    return out


def read_ru(rel: str) -> str:
    path = REPO / rel
    return path.read_text(encoding="utf-8-sig")


def count_words(token: str) -> int:
    return len(WORD_RE.findall(token))


def is_cyrillic_id(token: str) -> bool:
    return bool(CYRILLIC_RE.search(token))


def is_compound(token: str) -> bool:
    """Has 2+ word-parts in CamelCase sense."""
    return count_words(token) >= 2


# Filter out BSL keywords (control flow, declarations).
RU_KEYWORDS = {
    "Процедура", "Функция", "КонецПроцедуры", "КонецФункции", "Экспорт",
    "Если", "Тогда", "Иначе", "ИначеЕсли", "КонецЕсли",
    "Пока", "Для", "Каждого", "Из", "По", "Цикл", "КонецЦикла",
    "Попытка", "Исключение", "КонецПопытки", "Возврат", "Продолжить", "Прервать",
    "Перем", "Знач", "Неопределено", "Истина", "Ложь", "Null", "NULL",
    "Новый", "И", "Или", "Не", "Область", "КонецОбласти",
}
EN_KEYWORDS = {
    "Procedure", "Function", "EndProcedure", "EndFunction", "Export",
    "If", "Then", "Else", "ElsIf", "EndIf",
    "While", "For", "Each", "In", "To", "Do", "EndDo",
    "Try", "Except", "EndTry", "Return", "Continue", "Break",
    "Var", "Val", "Undefined", "True", "False", "Null",
    "New", "And", "Or", "Not", "Region", "EndRegion",
}


def tokens(line: str, keywords: set[str]) -> list[str]:
    return [t for t in ID_RE.findall(line) if t not in keywords]


OUT = Path(r"C:/git/httpconnector-translations/untr/mined_overrides.txt")


SIG_RE = re.compile(
    r"^\s*(?:Procedure|Function|Процедура|Функция)\s+([A-Za-zА-Яа-яЁё_][A-Za-zА-Яа-яЁё0-9_]*)\s*\(([^)]*)\)",
    re.MULTILINE,
)


def extract_signatures(text: str) -> list[tuple[str, list[str]]]:
    """Return list of (name, [params]) in source order."""
    out = []
    for m in SIG_RE.finditer(text):
        name = m.group(1)
        params_raw = m.group(2)
        params: list[str] = []
        for part in params_raw.split(","):
            part = part.strip()
            if not part:
                continue
            # Strip "Val "/"Знач " prefix, drop default value after "="
            part = re.sub(r"^(?:Val|Знач)\s+", "", part)
            name_only = part.split("=", 1)[0].strip()
            # Sometimes params have leading "ByVal" etc — already stripped.
            params.append(name_only)
        out.append((name, params))
    return out


def main() -> None:
    # ru_id -> Counter of en_id
    mappings: dict[str, Counter] = defaultdict(Counter)

    for ru_rel, en_rel in PAIRS:
        ru_text = read_ru(ru_rel)
        en_text = read_old_en(en_rel)

        # Line-by-line with difflib alignment on identifier-stripped skeleton.
        ru_lines = ru_text.split("\n")
        en_lines = en_text.split("\n")

        # Build line-skeleton: keep punctuation/numbers, drop identifier word content.
        # Makes lines comparable despite language difference.
        def skel(line: str) -> str:
            return re.sub(ID_RE, "X", line)

        ru_sk = [skel(l) for l in ru_lines]
        en_sk = [skel(l) for l in en_lines]

        sm = difflib.SequenceMatcher(a=ru_sk, b=en_sk, autojunk=False)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op != "equal":
                continue
            for k in range(i2 - i1):
                ri, ej = i1 + k, j1 + k
                ru_ids = tokens(ru_lines[ri], RU_KEYWORDS)
                en_ids = tokens(en_lines[ej], EN_KEYWORDS)
                if not ru_ids or not en_ids or len(ru_ids) != len(en_ids):
                    continue
                for ru_tok, en_tok in zip(ru_ids, en_ids):
                    if not is_cyrillic_id(ru_tok):
                        continue
                    if is_cyrillic_id(en_tok):
                        continue
                    if ru_tok == en_tok:
                        continue
                    mappings[ru_tok][en_tok] += 1

    # Filter to compound identifiers (>=2 word parts in RU).
    high: list[tuple[str, str, int, int]] = []  # (ru, en, wins, total)
    med: list[tuple[str, str]] = []              # (ru, en) — single observation
    low: list[tuple[str, list[tuple[str, int]], int]] = []

    for ru, cnt in mappings.items():
        if not is_compound(ru):
            continue
        total = sum(cnt.values())
        most, wins = cnt.most_common(1)[0]
        # HIGH — >=2 consistent observations AND >=80% agreement.
        # MED  — single observation with no conflicts.
        # LOW  — conflicting observations.
        if wins >= 2 and wins / total >= 0.8:
            high.append((ru, most, wins, total))
        elif total == 1:
            med.append((ru, most))
        else:
            low.append((ru, cnt.most_common(), total))

    high.sort(key=lambda r: r[0].lower())
    med.sort(key=lambda r: r[0].lower())
    low.sort(key=lambda r: r[0].lower())

    lines: list[str] = []
    lines.append(f"# HIGH-confidence mappings ({len(high)} entries) - >=2 observations, >=80% agreement")
    lines.append("# These are safe to auto-apply.")
    lines.append("")
    for ru, en, wins, total in high:
        tag = "" if wins == total else f"  # {wins}/{total}"
        lines.append(f"{ru}={en}{tag}")

    lines.append("")
    lines.append(f"# MEDIUM-confidence mappings ({len(med)} entries) - single observation, no conflicts")
    lines.append("# Review manually before applying.")
    lines.append("")
    for ru, en in med:
        lines.append(f"{ru}={en}")

    lines.append("")
    lines.append(f"# LOW-confidence mappings ({len(low)} entries) - conflicting observations")
    lines.append("")
    for ru, options, total in low:
        formatted = ", ".join(f"{en}x{w}" for en, w in options)
        lines.append(f"# {ru}  total={total}  candidates=[{formatted}]")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}  high={len(high)}  med={len(med)}  low={len(low)}")


if __name__ == "__main__":
    main()
