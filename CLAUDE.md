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
