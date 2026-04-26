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

# Russian literals that phase-1 restore must LEAVE TRANSLATED (skip the
# line-aligned revert). These are struct-key / list-of-names literals that
# the code reads/writes with English keys elsewhere — restoring them to
# Russian would break runtime lookups. Without this list, phase-1 reverts
# them and phase-2 re-applies the English translation on every run (stable
# output but wasted work). Listing them here makes the pipeline a true
# single-pass fixed point.
RESTORE_EXCEPTIONS = frozenset({
    "Наименование,Значение",
    "Наименование, Значение",
    "Пользователь, Пароль",
    "Пользователь, Пароль, Тип",
    "Имя,Данные,ИмяФайла",
    "Файлы,Данные",
    "УникальныйИдентификатор,ДвоичныеДанные",
})

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
    # HTTP method literals inside OverrideMethod (redirect 302/303 handler) —
    # camelcase dict case-folded "HEAD"→"Head" and "GET"→"Get". Without this,
    # after a 302/303 the module sends "Get" as HTTP method → server returns
    # 400 Bad Request. Affects Test_GetSuccessfulRedirectAbsoluteAddress,
    # Test_GetLoopedRedirect, Test_InstallCookies, Test_GetListReleasesInSite1.
    ('Method <> "Head"',        'Method <> "HEAD"'),
    ('Method = "Get";',         'Method = "GET";'),
    ('Upper(Method) <> "Head"', 'Upper(Method) <> "HEAD"'),
    # Default method in NewResponse() placeholder
    ('Insert("Method", "Get")', 'Insert("Method", "GET")'),

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
    ("КлиентскийСертификат",   "ClientCertificate"),
    ("КодыСостояний",          "StatusCodes"),
    ("СертификатКлиентаФайл",  "FileClientCertificate"),
    ("СертификатКлиентаWindows", "WindowsClientCertificate"),

    # --- EDT auto-prefixes Var_ to `Ключ` param/local to avoid conflict.
    # Old hand-translation used Key_ (with trailing underscore) everywhere —
    # both as HMAC's exported param (API contract) and as local variables.
    # Key_ is a valid BSL identifier, so blanket rewrite is safe.
    ("Var_Key", "Key_"),

    # --- PredefinedValue() enum path must be English on EN platform.
    # Phase-1 literal-restore sees the string literal on the RU line and
    # reverts EDT's correct English translation. Force it back here.
    (
        'PredefinedValue("ВариантЗаписиДатыJSON.УниверсальнаяДата")',
        'PredefinedValue("JSONDateWritingVariant.UniversalDate")',
    ),

    # --- Revert the wrong FromBeginning fix (EDT's FromBegin is actually correct) ---
    (".FromBeginning)",  ".FromBegin)"),
    (".FromBeginning,",  ".FromBegin,"),
    (".FromBeginning ",  ".FromBegin "),

    # --- HashFunction.SHA256 — dict had SHA256=sha256 (lowercase), actual enum is SHA256 ---
    (".sha256",              ".SHA256"),
    # Authorization header value: "AWS4-HMAC-SHA256" (uppercase SHA256 required)
    ('"AWS4-HMAC-sha256',    '"AWS4-HMAC-SHA256'),
    # --- Type-code literal compared via Lower(). RU has "aws4-hmac-sha256" (all lower);
    # camelcase dict tokenizer matches `aws4` → AWS4 and/or `sha256` → SHA256 depending
    # on dict entry ordering, producing one of several mixed-case variants. All of them
    # break the Lower()==literal comparison → AWS4-branch of PrepareAuthentication never
    # fires and x-amz-content-sha256 header stays empty. Cover every variant observed. ---
    ('"AWS4-hmac-sha256"',   '"aws4-hmac-sha256"'),
    ('"AWS4-hmac-SHA256"',   '"aws4-hmac-sha256"'),
    ('"aws4-hmac-SHA256"',   '"aws4-hmac-sha256"'),
    ('"AWS4-HMAC-sha256"',   '"aws4-hmac-sha256"'),
    # --- x-amz-content-sha256 is an HTTP HEADER name; AWS requires lowercase in
    # the canonical/signed headers list. Camelcase dict case-folds the `sha256`
    # fragment to `SHA256` via the `SHA256=SHA256` identifier entry. That breaks
    # the Authorization header signature comparison in Test_AuthenticationAWS4_*:
    # module builds SignedHeaders via Lower(key) (lowercase), test's expected
    # literal contains the case-folded `SHA256` (uppercase) — never equal. Revert
    # header-name occurrences (both bare and `-` suffix) to lowercase. ---
    ('x-amz-content-SHA256', 'x-amz-content-sha256'),

    # --- Struct-key / list-of-names literals — safety net for the RESTORE_EXCEPTIONS
    # set. Normal flow: EDT translates them correctly, phase-1 leaves them alone
    # (listed in RESTORE_EXCEPTIONS), phase-2 finds nothing to do. If something
    # regresses (manual edit / unexpected EDT output), these pairs catch it. ---
    ('"Наименование,Значение"',         '"Name,Value"'),
    ('"Наименование, Значение"',        '"Name, Value"'),
    ('"Пользователь, Пароль"',          '"User, Password"'),
    ('"Пользователь, Пароль, Тип"',     '"User, Password, Type"'),
    ('"Имя,Данные,ИмяФайла"',           '"Name,Data,NameFile"'),
    ('"Файлы,Данные"',                  '"Files,Data"'),
    ('"УникальныйИдентификатор,ДвоичныеДанные"', '"UUID,BinaryData"'),

    # --- Single-word data literals inconsistent with URL restores.
    # Phase 2 restored "Программист" inside URL literal but left bare "Programmer"
    # (single-word, identifier-like). Server echoes what client sends → test assertion
    # expecting "Programmer" fails. Restore the assertion side to Russian for
    # consistency. Similarly for "Hello, World" / "Привет, Мир". ---
    ('"Programmer"',      '"Программист"'),
    ('"Hello, World"',    '"Привет, Мир"'),
    ('"Hello, World!"',   '"Привет, Мир!"'),

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

    # --- NewParameters() Returns block — EDT's .trans generator produces no per-field
    # keys here because the doc has a duplicate `// Возвращаемое значение:` inside a
    # nested callback block (RU source deliberately keeps both occurrences). Full-line
    # translations for the 25 Cyrillic doc-comment lines. Field names mirror the
    # translated Parameters.Insert("<Name>", ...) keys. ---
    ("//  Структура - позволяет задать дополнительные параметры:",
     "//  Structure - allows specifying additional parameters:"),
    ("//    * Заголовки - Соответствие - см. описание Сессия.Заголовки.",
     "//    * Headers - Map - see description of Session.Headers."),
    ("//    * Аутентификация - Структура - см. описание Сессия.Аутентификация",
     "//    * Authentication - Structure - see description of Session.Authentication"),
    ("//    * Прокси - ИнтернетПрокси - см. описание Сессия.Прокси.",
     "//    * Proxy - InternetProxy - see description of Session.Proxy."),
    ("//    * ПараметрыЗапроса - Структура, Соответствие - см. описание Сессия.ПараметрыЗапроса.",
     "//    * ParametersRequest - Structure, Map - see description of Session.ParametersRequest."),
    ("//    * ПроверятьSSL - Булево - см. описание Сессия.ПроверятьSSL.",
     "//    * VerifySSL - Boolean - see description of Session.VerifySSL."),
    ("//    * КлиентскийСертификатSSL - СертификатКлиентаФайл, СертификатКлиентаWindows - Default value: Undefined.",
     "//    * ClientCertificateSSL - FileClientCertificate, WindowsClientCertificate - Default value: Undefined."),
    ("//    * Cookies - Массив - см. описание Сессия.Cookies.",
     "//    * Cookies - Array - see description of Session.Cookies."),
    ("//    * Таймаут - Число - время ожидания осуществляемого соединения и операций, в секундах.",
     "//    * Timeout - Number - timeout for the connection and operations, in seconds."),
    ("//        Значение по умолчанию - 30 сек.",
     "//        Default value - 30 sec."),
    ("//    * РазрешитьПеренаправление - Булево - Истина - редиректы будут автоматически разрешены.",
     "//    * AllowRedirect - Boolean - True - redirects will be automatically allowed."),
    ("//                                          Ложь - будет выполнен только один запрос к серверу.",
     "//                                          False - only a single request to the server will be made."),
    ("//    * Json - Структура, Соответствие - данные, которые необходимо сериализовать в JSON.",
     "//    * Json - Structure, Map - data to serialize to JSON."),
    ("//    * ПараметрыПреобразованияJSON - Структура - задает параметры преобразования JSON:",
     "//    * ParametersConversionJSON - Structure - specifies JSON conversion parameters:"),
    ("//        ** ПрочитатьВСоответствие - Булево - Если Истина, чтение объекта JSON будет выполнено в Соответствие.",
     "//        ** ReadInMap - Boolean - If True, JSON object reading will be done into Map."),
    ("//             Если Ложь, объекты будут считываться в объект типа Структура.",
     "//             If False, objects will be read into an object of type Structure."),
    ("//        ** ФорматДатыJSON - ФорматДатыJSON - формат, в котором представлена дата в строке,",
     "//        ** JSONDateFormat - JSONDateFormat - format in which the date is represented in the string,"),
    ("//             подлежащей преобразованию.",
     "//             to be converted."),
    ("//        ** ИменаСвойствСоЗначениямиДата -  Строка, Массив Из Строка - имена свойств JSON,",
     "//        ** NamesPropertiesWithDateValues -  String, Array Of String - JSON property names"),
    ("//             для которых нужно вызывать восстановление даты из строки.",
     "//             for which date restoration from string should be called."),
    ("//        ** ИмяФункцииВосстановления - Строка - определяет имя функции, которая будет вызывается при чтении",
     "//        ** NameFunctionRestore - String - specifies the name of the function that will be called when reading"),
    ("//            каждого свойства и должна иметь следующие параметры:",
     "//            each property and must have the following parameters:"),
    ("** Свойство - Строка - specified only when reading JSON objects",
     "** Property - String - specified only when reading JSON objects"),
    ("** Значение - Произвольный - value of a serializable type",
     "** Value - Arbitrary - value of a serializable type"),
    ("** ДополнительныеПараметры - Произвольный",
     "** AdditionalParameters - Arbitrary"),
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
    Line-by-line diff against RU source; restores only non-identifier literals.
    Literals listed in RESTORE_EXCEPTIONS are left translated so phase-2
    doesn't have to undo phase-1 work on every run."""
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
            if ru_lit in RESTORE_EXCEPTIONS:
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

    # Phase 1: restore Russian string literals that EDT mistranslated (test data).
    # Runs FIRST because phase-2 explicit replacements need to OVERRIDE restored
    # values for struct-key literals (e.g. "Наименование,Значение" → "Name,Value").
    # If we ran phase-2 last, phase-1 restore would ping-pong the struct keys back
    # to Russian even after phase-2 forces them English.
    print("phase 1 — literal restoration from RU source (line-aligned):")
    total_restored = 0
    for ru_path, en_path in LITERAL_RESTORE_PAIRS:
        n = restore_literals(ru_path, en_path)
        if n:
            print(f"  {en_path.relative_to(PROJ)} - restored {n} literal(s)")
            total_restored += n
    print(f"TOTAL phase-1 restorations: {total_restored}\n")

    # Phase 2: explicit identifier/literal substitutions (run AFTER restore so
    # hard-coded pairs win over auto-restore for struct-key literals).
    print("phase 2 — explicit substitutions:")
    grand_total = 0
    for f in bsl_files:
        count, applied = patch_file(f)
        if count:
            rel = f.relative_to(PROJ)
            print(f"{rel} - {count} replacement(s):")
            for line in applied:
                print(line)
            grand_total += count

    print(f"\nTOTAL phase-2 replacements: {grand_total}")


if __name__ == "__main__":
    main()
