# 1c-translations-with-model

Translation project for 1C:Enterprise configurations and extensions using EDT LanguageTool (dependent translation) format.
Covers both **interface** strings (`.lstr`) and **object model** documentation (`.trans`).

## Project overview

A **dependent translation project** is a standalone EDT project that provides translations for a source (parent) configuration or extension. It contains no metadata of its own — only translation dictionaries. Multiple translation projects can target the same source project (one per language).

This repository is format-agnostic and not bound to any specific configuration or extension. The same rules apply to:
- translations of main configurations (ERP, TMWE, UT, Drive, etc.)
- translations of extensions
- translations into any target language supported by EDT

### Translation project layout

```
<project>_<lang>/
├─ DT-INF/DEPENDENT.PMF         # links this project to its source (Parent-Project)
├─ .project                     # EDT project descriptor
└─ src/
   ├─ Configuration/
   │  ├─ Configuration_<lang>.lstr    # root config interface
   │  └─ Configuration_<lang>.trans   # root config model (description, vendor)
   ├─ CommonModules/<Name>/
   │  ├─ <Name>_<lang>.lstr           # module synonym
   │  ├─ Module_<lang>.lstr           # NStr strings from BSL code
   │  └─ Module_<lang>.trans          # method/param/return descriptions
   ├─ DataProcessors/<Name>/...       # same pattern
   ├─ Languages/<LangObject>/         # target language object(s)
   ├─ common_<lang>.dict              # shared word-level dictionary
   └─ common-camelcase_<lang>.dict    # shared CamelCase dictionary
```

Path under `src/` mirrors the source project's metadata layout.

## File formats

All three formats use java-properties syntax (`key=value`, `#comment`). They differ only by the header and what kinds of keys appear.

### `.lstr` — interface translations

Header: `#Translations for: interface`

Covers user-facing strings: object synonyms, attribute/tabular section names, form element titles, button commands, enum value names, and `NStr()` localizable strings extracted from BSL code.

```properties
#Translations for: interface

Synonym=Furnizori LLM
EnumValue.Mistral.Synonym=Mistral AI
Attribute.QueryText.Synonym=Text interogare
Method.КакИсключение.Var.ТекстИсключения.NStr.HTTP\ %1\ %2\n%3.Lines=HTTP %1 %2\n%3
```

### `.trans` — object model translations

Header: `#Translations for: model`

Covers documentation visible in the syntax helper and code completion: object/method descriptions, parameter descriptions, return value descriptions, and inline code-comment translations.

```properties
#Translations for: model

Description=Convenient HTTP client for 1C\:Enterprise 8
Vendor=Vladimir Bondarevskiy (vbondarevsky@gmail.com)
Method.Get.Description=Sends a GET request
Method.Get.Param.URL.Description=URL of the resource the request is sent to.
Method.Get.Return.Description=server response.
Method.Get.Comment.INFO\:\ authentication\ is\ ignored.Description=INFO\: authentication is ignored
```

### `.dict` — common dictionaries

Header: `#Translations for: common`

Project-wide word/phrase dictionary, reusable across files.

```properties
#Translations for: common

FAIL=FAIL
OK=OK
```

## Naming convention

- Interface: `<Name>_<lang>.lstr`
- Object model: `<Name>_<lang>.trans`
- Common dict: `common_<lang>.dict`, `common-camelcase_<lang>.dict`

`<lang>` is the target language code used by EDT (e.g., `en`, `ro`, `ru`). For a given source object, interface (`.lstr`) and model (`.trans`) files coexist side by side when both need translation.

## Escaping rules (apply to `.lstr`, `.trans`, and `.dict`)

Rules follow java-properties:

**In keys:**
- Space: `\ ` (backslash-space)
- Colon: `\:` (backslash-colon)
- Equals: `\=`

**In values:**
- Newline: `\n`
- Colon when literal: `\:`
- Backslash: `\\`
- Spaces and most characters: plain (no escaping)

**Placeholders** `%1`, `%2`, ... must be preserved as-is in translations (same count, same order when grammar allows).

## Key patterns

### `.lstr` (interface)

| Key prefix | Meaning |
|------------|---------|
| `Synonym` | Object display name |
| `Comment` | Object comment |
| `Attribute.<Name>.Synonym` | Attribute display name |
| `Attribute.<Name>.Title` | Form attribute title |
| `Attribute.<Name>.InputHint` | Input field placeholder |
| `TabularSection.<Name>.Synonym` | Tabular section name |
| `Command.<Name>.Title` | Form command (button) title |
| `Item.<Name>.Title` | Form element (group/decoration) title |
| `Form.<Name>.Synonym` | Form display name |
| `ObjectPresentation` | Object presentation |
| `ListPresentation` | List presentation |
| `EnumValue.<Name>.Synonym` | Enum value display name |
| `Language.<Name>.Synonym` | Language display name |
| `Method.<Name>.NStr.<EscKey>.Lines` | Localizable string from BSL code |
| `Method.<Name>.Var.<Var>.NStr.<EscKey>.Lines` | NStr inside a method variable |

### `.trans` (object model / documentation)

| Key prefix | Meaning |
|------------|---------|
| `Description` | Object description (root/configuration/module) |
| `Vendor` | Configuration vendor |
| `Method.<Name>.Description` | Method description (syntax helper) |
| `Method.<Name>.Param.<Name>.Description` | Parameter description |
| `Method.<Name>.Return.Description` | Return value description |
| `Method.<Name>.Return.<Field>.Description` | Field of return structure/object |
| `Method.<Name>.Param.<Name>.<Field>.Description` | Field of parameter structure |
| `Method.<Name>.Param.<Name>.Type.<Idx>.Description` | Typed overload description |
| `Method.<Name>.Comment.<EscKey>.Description` | Inline code-comment translation |
| `Region.<Path>.Comment.<EscKey>.Description` | Comment on a region |

## DT-INF/DEPENDENT.PMF

Every dependent translation project has this manifest linking it to its source:

```
Manifest-Version: 1.0
Parent-Project: <source-project-id>
```

`Parent-Project` must match the EDT project name of the source (parent) configuration or extension.

## Translation workflow

1. Source strings originate from metadata (`Synonym`, `Description`, …) or BSL code (`NStr()` calls, comments)
2. EDT LanguageTool extracts keys into `.lstr` / `.trans` / `.dict` files
3. Translator fills in values for each key in the target language
4. On EDT build, `dependentTranslationBuilder` compiles the dictionary into the deployable form
5. At runtime, 1C picks strings from the target-language dictionary when the user's locale matches

### Translation states

- **Translated** — value is in the target language
- **Source fallback** — value is still in the source language (Russian/English)
- **Missing key** — source has a key, target dictionary does not

## Rules for translating

1. **Never change keys** — only modify values (right side of `=`)
2. **Preserve the header** — first line must be `#Translations for: interface` / `model` / `common`
3. **Preserve blank line** between header and first entry
4. **Preserve placeholders** — `%1`, `%2`, etc. must remain in translations (same count and, when grammar allows, same order)
5. **Preserve key escaping** — `\ `, `\:`, `\=` in keys are part of the key
6. **Apply value escaping when needed** — `\n` for line breaks, `\:` for literal colons, `\\` for backslash
7. **Match file structure across languages** — corresponding `_<lang1>` and `_<lang2>` files must have identical key sets (same lines, same order) for the same source file
8. **Match file structure across formats** — `.lstr` and `.trans` are independent and cover different keys; do not merge
9. **Technical terms stay as-is** — brand names (OpenAI, ChromaDB), protocol names (HTTP, JSON, TLS), identifiers and code references are not translated
10. **UTF-8 encoding** — save files in UTF-8
11. **Line endings** — preserve existing line endings; do not introduce mixed CRLF/LF

## Comparing translations

To find missing or untranslated entries, diff the corresponding files across languages:

- Between languages: `<File>_ro.lstr` vs `<File>_ru.lstr` (same path in two translation projects)
- Between formats: `<File>_<lang>.lstr` vs `<File>_<lang>.trans` cover different keys — do not compare directly

Both language files must have identical key sets. If a target-language file is missing, create it with the same keys as the other language's file and translate.

## Tooling — translation pipeline

Repository includes scripts that automate a multi-phase translation of a new dependent translation project. They were developed against HTTPConnector/dictionaries_en but are generic — retarget paths in constants at the top of each script to apply to another project.

### Pipeline phases

**A — exact-key migration** (`migrate.py`): pair dict files between an old translation project (reference) and a new one; copy values for keys that match byte-for-byte across the pair. Preserves file structure (header, blank lines, EOL, BOM).

**B — alias-map migration** (`migrate_b.py`): parse BSL source of both en/ and ru/ copies, pair functions with identical names, zip parameters positionally → build a `ru_param → en_param` alias map. For each unmatched key in the new dict, translate Cyrillic tokens via the alias and look up the resulting English key in the old dict. Narrow but deterministic.

**C — manual translation** (`translations_*.py` + `apply_*.py`): for remaining untranslated entries, human- or LLM-provided values stored in Python `TR = {key: english_value}` dicts. The applier reads the target dict file line-by-line, replaces values for keys in TR, preserves file structure.

**camelcase tokenizer** (`camelcase_token_tr.py` + `apply_camelcase.py`): for `common-camelcase_<lang>.dict` where CamelCase composites combine Cyrillic and Latin parts (e.g., `GZipРазмерFooter`). Tokenizes each value, substitutes each Cyrillic token via a 600+ entry token dict, rejoins preserving Latin parts. Aborts with a report if any token lacks a translation.

**Post-build patcher** (`postbuild_patch.py`): see "EDT LanguageTool quirks" below — covers residuals that EDT refuses to translate via dictionaries. Must run after every EDT dependent-translation rebuild.

### Analysis scripts

- `analyze.py` — count matching keys across old/new dicts, show examples
- `estimate.py` — coverage analysis of alias-map vs doc-comment approaches
- `extract_untranslated.py` / `extract_all_untranslated.py` — list keys whose values still contain Cyrillic (work remaining)
- `camelcase_tokens.py` — tokenize CamelCase identifiers, count unique Cyrillic tokens
- `find_missing_dict_keys.py` — identifiers used in RU source missing as keys in dict
- `check_translated.py` / `check_translated2.py` — scan EDT-translated project for residual Cyrillic (code vs doc)

### Dict-layout helpers

- `sort_dict.py` — alphabetically sort entries of a dict file (EDT expects sorted order; appended-at-end entries may be ignored)
- `fix_regions.py` — normalize SSL/БСП standard region names to canonical English (`ПрограммныйИнтерфейс=Public`, `СлужебныеПроцедурыИФункции=Private`, `ОбработчикиСобытий=EventHandlers`, etc.)
- `fix_case.py` — normalize `PascalCase=lowercase` entries inherited from legacy dicts (`Cookie=cookie` → `Cookie=Cookie`, `Basic=basic` → `Basic=Basic`) — prevents "variable name must start with capital letter" warnings
- `fix_camelcase.py` — case-normalize HTTP method names (`Get=GET` → `Get=Get`, `Put=put` → `Put=Put`) and add project-specific missing identifiers
- `proper_split.py` / `move_to_common.py` / `move_back.py` / `move_remaining.py` / `final_revert.py` — experimental moves of entries between `common-camelcase_<lang>.dict` and `common_<lang>.dict` per EDT's `translation_storages.yml` filter rules (`camelcase: ONLY` vs `camelcase: NONE`)

## EDT LanguageTool quirks (learned)

Discovered while debugging HTTPConnector_en translation. Useful when the dependent-translation build leaves unexpected residuals.

### Storage classification and file roles

The source project's `.settings/translation_storages.yml` defines seven translation storages in read order. Key storages for dict files:

- **`common-camelcase_<lang>.dict`** — `feature_filter: camelcase: ONLY, model: ONLY` — **only CamelCase identifiers** (multi-word: `GetValue`, `MyFunction`, `НоваяCookie`)
- **`common_<lang>.dict`** — `feature_filter: camelcase: NONE, model: ONLY` — **only non-CamelCase** (single-word: `Имя`, `Данные`; platform keywords)
- **`common_<lang>.lsdict`** — interface-side common (rare)

**Consequence:** a single-word identifier like `Имя=Name` placed in `common-camelcase_<lang>.dict` will be IGNORED by EDT. Move it to `common_<lang>.dict`. Use `proper_split.py` or similar.

### Sorted order matters

EDT may ignore dict entries that appear after a blank line or out of alphabetical order. Always keep dict files sorted. `sort_dict.py` does this.

### Case-normalization of values

Legacy dicts migrated from old projects sometimes have lowercase values for PascalCase keys (`Cookie=cookie`, `Put=put`). When EDT applies these as identifiers, it produces variables like `cookies`, `put` — which trigger BSL validation warnings. Normalize values to match the key case (`fix_case.py`).

### Standard region names (SSL/БСП)

EDT expects canonical English region names per SSL standard:

| Russian | English (canonical) |
|---------|---------------------|
| `ПрограммныйИнтерфейс` | `Public` |
| `СлужебныйПрограммныйИнтерфейс` | `Internal` |
| `СлужебныеПроцедурыИФункции` | `Private` |
| `ОбработчикиСобытий` | `EventHandlers` |
| `ОбработчикиСобытийФормы` | `FormEventHandlers` |
| `ОбработчикиСобытийЭлементовШапкиФормы` | `FormHeaderItemsEventHandlers` |
| `ОбработчикиКомандФормы` | `FormCommandsEventHandlers` |

If a region translates to something non-canonical (like `ProgramInterface` or `HandlersEvents`), EDT issues "method should be placed in standard region Public/Internal/Private" warnings for every method in the region.

### Dict-generator gaps in `.trans`

For some methods, EDT's dict generator creates only `Method.X.Description` and `Method.X.Return.Description` keys, skipping per-field keys for sub-fields of the return structure. For similar methods with analogous doc format, it may generate 15+ per-field keys. A workaround: add the missing keys manually (`Method.X.Return.<Field>.Description`, etc.) — EDT will honor them on rebuild. See `add_newparams_keys.py` / `fix_newparams_finale.py` for examples.

**Trigger for generator to produce per-field keys**: the heading line of the Return structure description in the BSL doc comment must not repeat elsewhere in the block. In HTTPConnector, two `// Возвращаемое значение:` comments in one method's doc (one for the method itself, one for a nested callback) made the generator treat both as one context and produce only a single key. Renaming the nested one (e.g., to `// Возвращает значение:`) unblocked the generator.

### Translated project has both source and translation

`HTTPConnector_translated_project/src/` contains BOTH English-named modules (translation output) AND Russian-named copies (mirrored from source). When post-processing the translated project, restrict scope to paths without Cyrillic components — see the filter in `postbuild_patch.py`.

### Residuals and the post-build patcher

Even with correct dictionaries and sub-field keys, some identifiers or phrases remain untranslated after `dependentTranslationBuilder` runs. Observed cases include specific identifiers and doc-comment blocks inside nested callback parameters. Root cause unclear (likely an EDT incremental-build or generator quirk — no reliable dictionary-level fix found).

**`postbuild_patch.py`** is the pragmatic cover: it scans translated-project BSL files (English-path-only) and applies a table of literal Russian → English substitutions. Idempotent, deterministic, must be re-run after each EDT rebuild.

## Translation workflow for a new project

1. Import source project and create empty dependent translation project in EDT. EDT auto-generates `.lstr` / `.trans` / `.dict` files with source-language (Russian) placeholder values.
2. Phase A: if an older translation for the same source exists, run `migrate.py` to copy exact-key matches.
3. Phase B: run `migrate_b.py` to leverage positional alias map for common-named functions.
4. Manual: translate remaining entries. Use `extract_all_untranslated.py` to list them; produce `translations_<file>.py`; run `apply_*.py`.
5. Camelcase: if `common-camelcase_<lang>.dict` has Cyrillic values, run `apply_camelcase.py`.
6. Dict hygiene: `sort_dict.py`, `fix_regions.py`, `fix_case.py`, `fix_camelcase.py`.
7. Move entries to correct storage: `proper_split.py` (non-CamelCase → `common_<lang>.dict`).
8. Build translated project in EDT.
9. Scan residuals: `check_translated2.py`.
10. For gaps, add missing `.trans` sub-field keys (follow pattern from similar methods).
11. For unfixable residuals, populate `postbuild_patch.py` with replacement pairs and run after every rebuild.
12. Final verify: `check_translated2.py` — should report `CODE issues: 0  DOC issues: 0`.
