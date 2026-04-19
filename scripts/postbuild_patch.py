"""Post-build patcher for HTTPConnector_translated_project.

After EDT rebuilds the translated project, this script applies literal
text replacements to translated module files to cover residual Russian
fragments that EDT's LanguageTool doesn't translate via dictionaries
(3 stuck code identifiers + doc-comment blocks where EDT's generator
didn't produce sub-field keys).

Run this after every EDT dependent-translation rebuild.

Scope:
- Only patches translated project (HTTPConnector_translated_project).
- Never touches source project, dictionaries, or metadata.
- Idempotent — running twice is safe (second run finds nothing to replace).
"""
import re
from pathlib import Path

PROJ = Path(r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/HTTP connector/HTTPConnector_translated_project")

# Per-file RU source for literal restoration (EDT mistranslates some string
# literals via camelcase dict tokenization — test data literals like
# "Секретный ключ" → "Secret key" which breaks HMAC/byte tests).
LITERAL_RESTORE_PAIRS = [
    (
        Path(r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/HTTP connector/HTTPConnector_ru/src/DataProcessors/Тесты/ObjectModule.bsl"),
        PROJ / "src/DataProcessors/Tests/ObjectModule.bsl",
    ),
]

# (russian_source, english_target) — longest-first ordering matters for
# substring overlaps (e.g., match "повторы будут выполняться для конкретных
# кодов состояний." before the shorter prefix).
REPLACEMENTS = [
    # --- EDT platform dictionary has wrong English alias for СтрНачинаетсяС ---
    # EDT maps it to StrStartsWith but the actual platform English identifier
    # is StrStartWith (no "s" in "Start"). StrEndsWith is OK — leave alone.
    # At runtime the wrong form fails with
    # "Procedure or function with the specified name is not defined".
    # Match only call sites (with "(") — leaves comments intact.
    ("StrStartsWith(",  "StrStartWith("),
    # Also catch the Russian form (if earlier patcher run or dict change left it)
    ("СтрНачинаетсяС(", "StrStartWith("),

    # --- HTTP method literals translated by camelcase dict ---
    # EDT's camelcase dict translates "POST" → "Post", "GET" → "Get" inside
    # string literals (via token case-folding). These are HTTP method strings
    # passed to HTTPConnection.CallHTTPMethod — must stay uppercase per HTTP
    # spec (server returns 400 otherwise). Match the specific call-site pattern.
    ('CallHTTPMethod(CurrentSession, "Get",',     'CallHTTPMethod(CurrentSession, "GET",'),
    ('CallHTTPMethod(CurrentSession, "Options",', 'CallHTTPMethod(CurrentSession, "OPTIONS",'),
    ('CallHTTPMethod(CurrentSession, "Head",',    'CallHTTPMethod(CurrentSession, "HEAD",'),
    ('CallHTTPMethod(CurrentSession, "Post",',    'CallHTTPMethod(CurrentSession, "POST",'),
    ('CallHTTPMethod(CurrentSession, "Put",',     'CallHTTPMethod(CurrentSession, "PUT",'),
    ('CallHTTPMethod(CurrentSession, "Patch",',   'CallHTTPMethod(CurrentSession, "PATCH",'),
    ('CallHTTPMethod(CurrentSession, "Delete",',  'CallHTTPMethod(CurrentSession, "DELETE",'),
    ('CallHTTPMethod(CurrentSession, "Mkcol",',   'CallHTTPMethod(CurrentSession, "MKCOL",'),

    # --- Platform object fields with wrong positional translation ---
    # Tokenizer reverses word order; platform names differ. Fix access sites
    # (.Name) and literals ("Name"). If dict is fixed via fix_platform_fields.py,
    # these are no-ops on next rebuild — they remain as safety net.
    (".CodeStatus",              ".StatusCode"),
    ('"CodeStatus"',             '"StatusCode"'),
    (".BreakLines",              ".NewLines"),            # JSONWriterSettings
    ('"BreakLines"',             '"NewLines"'),
    (".SymbolsIndent",           ".PaddingSymbols"),      # JSONWriterSettings
    ('"SymbolsIndent"',          '"PaddingSymbols"'),
    (".EscapeSeparatorsLines",   ".EscapeLineTerminators"),
    ('"EscapeSeparatorsLines"',  '"EscapeLineTerminators"'),
    (".AddressResource",         ".ResourceAddress"),     # HTTPRequest
    ('"AddressResource"',        '"ResourceAddress"'),
    (".UseAuthenticationOS",     ".UseOSAuthentication"), # InternetProxy
    ('"UseAuthenticationOS"',    '"UseOSAuthentication"'),

    # --- CODE identifiers EDT refused to translate from dict ---
    ("ПрочитатьZip",           "ReadZip"),
    ("НоваяCookie",            "NewCookie"),
    ("ОбработчикиКомандФормы", "FormCommandsEventHandlers"),

    # --- Long multi-line doc blocks (more specific first) ---
    (
        "* МодульФункцииВосстановления - Произвольный - определяет модуль, процедура которого будет использована для\r\n//         восстановления значения.",
        "* ModuleFunctionRestore - Arbitrary - specifies the module whose procedure will be used for\r\n//         value restoration.",
    ),
    (
        "* МодульФункцииВосстановления - Произвольный - определяет модуль, процедура которого будет использована для\r\n//             восстановления значения.",
        "* ModuleFunctionRestore - Arbitrary - specifies the module whose procedure will be used for\r\n//             value restoration.",
    ),
    (
        "* ДополнительныеПараметрыФункцииВосстановления - Произвольный - определяет дополнительные параметры, которые\r\n//         будут переданы в функцию восстановления значений.",
        "* AdditionalParametersFunctionRestore - Arbitrary - specifies additional parameters that\r\n//         will be passed to the value restoration function.",
    ),
    (
        "* ДополнительныеПараметрыФункцииВосстановления - Произвольный - определяет дополнительные параметры, которые\r\n//             будут переданы в функцию восстановления значений.",
        "* AdditionalParametersFunctionRestore - Arbitrary - specifies additional parameters that\r\n//             will be passed to the value restoration function.",
    ),
    (
        "* ИменаСвойствДляОбработкиВосстановления - Массив - определяет массив имен свойств JSON, для которых\r\n//         будет вызвана функция восстановления.",
        "* NamesPropertiesForProcessingRestore - Array - specifies an array of JSON property names for which\r\n//         the restoration function will be called.",
    ),
    (
        "* ИменаСвойствДляОбработкиВосстановления - Массив - определяет массив имен свойств JSON, для которых\r\n//             будет вызвана функция восстановления.",
        "* NamesPropertiesForProcessingRestore - Array - specifies an array of JSON property names for which\r\n//             the restoration function will be called.",
    ),
    (
        "* МаксимальнаяВложенность - Число - определяет максимальный уровень вложенности объекта JSON.",
        "* MaxNesting - Number - specifies the maximum nesting level of the JSON object.",
    ),
    (
        "- Structure, Map - поля формы, которые необходимо отправить в запрос:",
        "- Structure, Map - form fields to send in the request:",
    ),
    (
        "Data - String, BinaryData - произвольные данные, которые необходимо отправить в запросе.",
        "Data - String, BinaryData - arbitrary data to send in the request.",
    ),
    (
        "RetryForCodesStatus - Undefined - повторы будут выполняться для кодов состояний >= 500.",
        "RetryForCodesStatus - Undefined - retries are performed for status codes >= 500.",
    ),
    (
        "- Array - повторы будут выполняться для конкретных кодов состояний.",
        "- Array - retries are performed for specific status codes.",
    ),
    (
        "Files - См. НовыйОтправляемыйФайл, Array of See NewSentFile - files to send",
        "Files - See NewSentFile, Array of See NewSentFile - files to send",
    ),

    # --- Short doc phrases ---
    ("Возвращаемое значение:",           "Returns:"),
    ("Возвращает значение:",             "Returns:"),
    ("Произвольный - значение, десериализованное из JSON.",
                                          "Arbitrary - value deserialized from JSON."),
    ("указывается только при чтении объектов JSON",
                                          "specified only when reading JSON objects"),
    ("значение допустимого для сериализации типа",
                                          "value of a serializable type"),
    ("Key - String - имя поля.",         "Key - String - field name."),
    ("Value - String - значение поля.",  "Value - String - field value."),
    ("Значение по умолчанию: Неопределено.",
                                          "Default value: Undefined."),
    ("- Истина - the value of CACertificatesOS is used.",
                                          "- True - the value of CACertificatesOS is used."),
    ("* Метод - String - HTTP request verb name",
                                          "* Method - String - HTTP request verb name"),
]


def patch_file(path: Path) -> tuple[int, list[str]]:
    """Apply replacements to one BSL file. Returns (replacement_count, list_of_applied).

    Normalizes line endings to \\n during matching so patterns are EOL-agnostic,
    then restores the original EOL when writing back.
    """
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    body = raw[3:] if has_bom else raw

    text = body.decode("utf-8")
    # Detect and normalize EOL
    had_crlf = "\r\n" in text
    if had_crlf:
        text = text.replace("\r\n", "\n")

    total = 0
    applied = []
    for src, dst in REPLACEMENTS:
        # Normalize replacement patterns too
        src_n = src.replace("\r\n", "\n")
        dst_n = dst.replace("\r\n", "\n")
        if src_n not in text:
            continue
        n = text.count(src_n)
        text = text.replace(src_n, dst_n)
        total += n
        short = src_n[:60].replace("\n", " | ")
        applied.append(f"  x{n}: {short}{'...' if len(src_n) > 60 else ''}")

    if total == 0:
        return 0, []

    # Restore CRLF if original had it
    if had_crlf:
        text = text.replace("\n", "\r\n")

    new_raw = text.encode("utf-8")
    if has_bom:
        new_raw = b"\xef\xbb\xbf" + new_raw
    path.write_bytes(new_raw)
    return total, applied


# --- Literal restoration (phase 2) ---

_LIT = re.compile(r'"([^"]*)"')
_CYR = re.compile(r"[А-Яа-яЁё]")


def _is_identifier_like(s: str) -> bool:
    """Pure-identifier literals (procedure names for Execute, struct key lists
    like 'Name, Value') — these SHOULD stay translated, skip restoration."""
    if re.search(r"[ \-!?|%&?=:/<>]", s):
        compact = re.sub(r",\s*", "", s)
        if re.match(r"^[A-Za-zА-Яа-яЁё0-9_]+$", compact):
            return True
        return False
    return bool(re.match(r"^[A-Za-zА-Яа-яЁё0-9_]+$", s))


def restore_literals(ru_path: Path, en_path: Path) -> int:
    """Revert EDT's tokenized translation of Russian string literals that
    represent test/data content (not procedure names or struct keys).
    Line-by-line diff against RU source; restores only non-identifier literals."""
    if not ru_path.exists() or not en_path.exists():
        return 0

    raw_en = en_path.read_bytes()
    has_bom = raw_en.startswith(b"\xef\xbb\xbf")
    body_en = raw_en[3:] if has_bom else raw_en
    text_en = body_en.decode("utf-8")
    had_crlf = "\r\n" in text_en
    if had_crlf:
        text_en = text_en.replace("\r\n", "\n")

    ru_text = ru_path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    en_lines = text_en.split("\n")
    ru_lines = ru_text.split("\n")

    reverted = 0
    out_lines = []
    for i, en_line in enumerate(en_lines):
        if i >= len(ru_lines):
            out_lines.append(en_line)
            continue
        ru_lits = _LIT.findall(ru_lines[i])
        en_lits = _LIT.findall(en_line)
        if len(ru_lits) != len(en_lits):
            out_lines.append(en_line)
            continue
        new_line = en_line
        for ru_lit, en_lit in zip(ru_lits, en_lits):
            if ru_lit == en_lit or not _CYR.search(ru_lit) or _is_identifier_like(ru_lit):
                continue
            new_line = new_line.replace(f'"{en_lit}"', f'"{ru_lit}"', 1)
            reverted += 1
        out_lines.append(new_line)

    out_text = "\n".join(out_lines)
    if had_crlf:
        out_text = out_text.replace("\n", "\r\n")
    out_raw = out_text.encode("utf-8")
    if has_bom:
        out_raw = b"\xef\xbb\xbf" + out_raw
    en_path.write_bytes(out_raw)
    return reverted


def main():
    import sys
    # Force UTF-8 output for non-ASCII identifiers in console (Windows cp1251 default).
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # Translated project contains BOTH the EN-named modules (translation output)
    # AND RU-named copies (synced from source). Patch only the EN-named ones —
    # i.e., files whose path has no Cyrillic components.
    CYR = re.compile(r"[А-Яа-яЁё]")
    bsl_files = [f for f in PROJ.rglob("*.bsl") if not CYR.search(str(f.relative_to(PROJ)))]
    print(f"scanning {len(bsl_files)} English-path BSL files in {PROJ}\n")

    grand_total = 0
    for f in bsl_files:
        count, applied = patch_file(f)
        if count:
            rel = f.relative_to(PROJ)
            print(f"{rel} - {count} replacement(s):")
            for line in applied:
                print(line)
            grand_total += count

    print(f"\nTOTAL phase-1 replacements: {grand_total}")

    # Phase 2: restore Russian string literals that EDT mistranslated (test data).
    print("\nphase 2 — literal restoration (line-aligned against RU source):")
    total_restored = 0
    for ru_path, en_path in LITERAL_RESTORE_PAIRS:
        n = restore_literals(ru_path, en_path)
        if n:
            print(f"  {en_path.relative_to(PROJ)} - restored {n} literal(s)")
            total_restored += n
    print(f"\nTOTAL phase-2 restorations: {total_restored}")


if __name__ == "__main__":
    main()
