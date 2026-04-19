# Post-build patcher — why it exists

`postbuild_patch.py` is a Python script that rewrites parts of the translated project's BSL files after EDT's dependent-translation build. It exists because EDT's LanguageTool has several behaviors that **cannot be fixed by dictionary edits alone**.

This document explains the specific failure modes that forced a post-process step and describes the logic of each mitigation.

## TL;DR

EDT's translation applies a per-word dictionary to **every occurrence of a token**, including:

- Identifier renames (desired)
- Region names (desired)
- **String literal contents** (not desired)
- **String literals that need to stay in the source language** (HTTP verbs, platform format directives, byte-level test data, etc.)

Because the dictionary is **context-blind**, a single entry governs both "translate identifier `Post` to `Post`" and "translate literal `"POST"` to `"Post"`" — these have opposite requirements. `postbuild_patch.py` fixes the fallout in the translated output where the dict can't.

## Failure mode #1 — EDT platform dictionary has wrong English aliases for some built-ins

### What goes wrong

EDT ships a built-in "platform context" dictionary mapping Russian platform identifiers to their English aliases. For **some** built-ins this mapping is incorrect:

| Russian | EDT maps to (wrong) | Actual 1C platform English name |
|---------|---------------------|-----------------------------------|
| `СтрНачинаетсяС` | `StrStartsWith` | `StrStartWith` (no "s" in "Start") |

EDT's compile-time validation accepts the wrong name (it trusts its own mapping). At **runtime** the wrong form fails with:

```
Procedure or function with the specified name is not defined (StrStartsWith)
```

Note: `СтрЗаканчиваетсяНа` → `StrEndsWith` IS correct (with "s"). The pattern is asymmetric — don't blindly transform both.

### Why the dict can't fix it alone

We added `СтрНачинаетсяС=StrStartWith` to `common-camelcase_en.dict`. User-dict has higher priority than platform context, so future EDT builds use the correct name. **That's the permanent fix.**

But:
- Intermediate builds (before the user-dict entry is picked up) produce wrong output.
- If EDT regenerates the dict file (rare but possible), the override may be lost.
- If developer adds new code using `СтрНачинаетсяС` without regenerating the dict, EDT's platform default kicks in again.

So the patcher keeps a safety net: rewrite `StrStartsWith(` → `StrStartWith(` at call-sites. Matched with trailing `(` so comments/identifiers aren't touched.

## Failure mode #2 — camelcase dict translates string literal contents

### What goes wrong

EDT's camelcase dict is used to translate **BSL identifiers** (CamelCase composites). But EDT also **tokenizes string literal contents** against the same dict and replaces matched tokens.

Example — Russian test source:

```bsl
Ключ = ПолучитьДвоичныеДанныеИзСтроки("Секретный ключ", КодировкаТекста.UTF8, Ложь);
Данные = ПолучитьДвоичныеДанныеИзСтроки("Какие-то данные", КодировкаТекста.UTF8, Ложь);
```

Dict has tokens like `Секретный=Secret`, `ключ=key`, `Какие=Which`, `то=then`, `данные=data`. After EDT translation:

```bsl
Var_Key = GetBinaryDataFromString("Secret key", TextEncoding.utf8, False);
Data = GetBinaryDataFromString("Which-then data", TextEncoding.utf8, False);
```

For tests that compare bytes (HMAC, hash, URL-encoded content), this **changes the bytes** passed to the hash function and breaks assertions:

```
<80 6D 4A D3 ...> not equals <1B 1E C4 16 ...>
```

### Why the dict can't fix it alone

The problematic tokens (`Секретный`, `ключ`, `данные`, etc.) are legitimate parts of **real identifiers** (`СекретныйКлюч=SecretKey`, `ДвоичныеДанные=BinaryData`, etc.). Removing token-level entries breaks identifier translation for any composite that doesn't have an explicit full-identifier entry. In HTTPConnector's dict of ~1100 entries, the vast majority rely on the tokenization fallback.

EDT provides no way to limit a dictionary's scope to identifiers only.

### How the patcher handles it

`restore_literals()` in phase 2 of `postbuild_patch.py`:

1. Line-aligned diff of translated file against the RU source.
2. For each line with a string literal that differs between RU and EN versions, compare:
   - If RU literal has no Cyrillic → leave translated (was already English, nothing to restore)
   - If RU literal is an "identifier-like" literal (pure `[A-Za-z0-9_]+`, optionally `,` + `\s`) → leave translated — these are usually procedure names for `Execute()` or struct key lists that must match consistently
   - Otherwise → revert EN literal to RU original

Configure `LITERAL_RESTORE_PAIRS` with `(ru_path, en_path)` tuples for each module that has test-data literals.

## Failure mode #3 — HTTP method literals case-folded

### What goes wrong

Same tokenization mechanism as failure mode #2, but the affected literals are **identifier-like** so the literal-restore heuristic doesn't catch them.

RU source:

```bsl
Возврат ВызватьHTTPМетод(ТекущаяСессия, "POST", URL, Параметры);
```

Dict has `Post=Post` (PascalCase — correct for BSL function name). EDT case-insensitively matches the literal `"POST"` against token `Post` and outputs the dict value `Post`:

```bsl
Return CallHTTPMethod(CurrentSession, "Post", URL, Parameters);
```

`"Post"` is then sent as the HTTP method verb. HTTP servers are case-sensitive per spec (RFC 7230); nginx returns `400 Bad Request`.

### Why the dict can't fix it alone

Setting `Post=POST` would make BSL identifier `Post` translate to `POST`, producing ugly function declarations (`Function POST(...)`). Setting `Post=Post` keeps function names pretty but breaks literal `"POST"`.

Same fundamental problem as failure mode #2 — dict cannot distinguish identifier vs string-literal context.

### How the patcher handles it

Explicit context-matched replacements scoped to `CallHTTPMethod(...)` sites:

```python
('CallHTTPMethod(CurrentSession, "Get",',  'CallHTTPMethod(CurrentSession, "GET",'),
('CallHTTPMethod(CurrentSession, "Post",', 'CallHTTPMethod(CurrentSession, "POST",'),
# ...for each HTTP verb
```

The preceding `CallHTTPMethod(CurrentSession, ` anchor narrows the match — arbitrary `"Post"` elsewhere in the file stays untouched.

## Failure mode #4 — platform object fields whose English name isn't the positional token-translation

### What goes wrong

`common-camelcase_en.dict` builds composite translations by concatenating token translations in the **same order** as the Russian. Many platform object property/method names don't follow this word order:

| Russian | Positional translation (wrong) | Actual platform English name |
|---------|--------------------------------|------------------------------|
| `КодСостояния` | `CodeStatus` | `StatusCode` |
| `ПереносСтрок` | `BreakLines` | `NewLines` |
| `СимволыОтступа` | `SymbolsIndent` | `PaddingSymbols` |
| `ЭкранироватьРазделителиСтрок` | `EscapeSeparatorsLines` | `EscapeLineTerminators` |
| `АдресРесурса` | `AddressResource` | `ResourceAddress` |
| `ИспользоватьАутентификациюОС` | `UseAuthenticationOS` | `UseOSAuthentication` |

When the translated module accesses a platform object field with the wrong name, runtime throws:

```
Object field not found (CodeStatus)
```

### Why the dict can't fix it alone

It CAN fix it — by adding an explicit full-identifier override (`КодСостояния=StatusCode`). We do that (`fix_platform_fields.py`). But:

- We only discover the mismatches when a test fails with "Object field not found". It's reactive, not exhaustive.
- If developer adds new code using a newly-encountered composite like `ОчередьОбработки` (hypothetical `ProcessingQueue` but EDT translates to `QueueProcessing`), it breaks silently until tested.

So the patcher carries a parallel list of access-site rewrites (`.CodeStatus` → `.StatusCode`, `"CodeStatus"` → `"StatusCode"`, etc.) as an independent safety net. The dict fix is primary; the patcher is belt-and-suspenders.

## Failure mode #5 — EDT dict generator skips sub-field keys for some methods

### What goes wrong

For some methods, EDT's `.trans` dictionary generator produces only `Method.X.Description` and `Method.X.Return.Description` keys, skipping per-field keys (`Method.X.Return.<FieldName>.Description`) that it generates for structurally-similar methods.

Result: large blocks of Russian text remain in the translated module's doc comments for the affected method.

### Why the dict can't fix it alone

Missing keys can be added manually to `.trans` and EDT does honor them on rebuild (we verified this). Primary fix is a RU-source edit that unblocks the generator (e.g., renaming a duplicate `// Возвращаемое значение:` line in a nested callback) plus manually-added sub-field keys.

The patcher doesn't currently handle this class — it's addressed at dict generation time (see `add_newparams_keys.py`, `fix_newparams_finale.py`). Listed here for completeness.

## Why two phases?

`postbuild_patch.py` splits work into two passes:

- **Phase 1 — identifier/literal substitutions.** Plain string-pair replacements. Deterministic, fast, idempotent. Handles failure modes #1, #3, #4.

- **Phase 2 — literal restoration from RU source.** For modules whose RU source is an authority for string-literal content (test modules, primarily), do a line-aligned diff and revert non-identifier-like Russian literals. Handles failure mode #2.

The two phases are independent and composable per-file.

## When to extend

- **New runtime `not defined` error for a platform built-in** — add to failure mode #1's pair list AND to `fix_str_builtins.py` overrides.
- **New test assertion failing on byte comparison** — register the module's `(ru_path, en_path)` pair in `LITERAL_RESTORE_PAIRS`.
- **New `Object field not found` error** — confirm the actual platform English name, add to `fix_platform_fields.py` overrides AND to phase-1 pair list.
- **New test failing with server `400 Bad Request` on HTTP call** — likely another HTTP verb / protocol token mangled by case-folding; add a context-anchored pair to the HTTP-verb block.

Each extension follows the same pattern: verify the correct English form (via `get_platform_documentation` or 1C docs), add an explicit dict override where possible, and a patcher safety-net replacement.

## Guidance for applying to a new project

1. Clone `postbuild_patch.py`.
2. Retarget `PROJ` and `LITERAL_RESTORE_PAIRS` to the new project's paths.
3. Start with the HTTP-verb block and platform-field block — they're project-independent in their failure pattern (any 1C configuration using HTTP will need them).
4. Run after each EDT rebuild. Re-run when new runtime errors surface; add pairs as they appear.
5. Keep the patcher idempotent — every replacement should be a no-op on the second run.
