# HTTPConnector Translations

Pipeline for keeping the English translation of the [HTTPConnector](https://github.com/vbondarevsky/Connector) library in sync with its Russian source. Built on EDT's LanguageTool ("dependent translation project") feature plus a set of scripts that fill the gaps automatic generation leaves behind.

> **Documentation language**: this is the English version. The Russian (primary) version is at [README.md](README.md).

## About

The original HTTPConnector library is developed in Russian. The English translation was originally hand-written in PR #79 (2021), but the RU source has evolved significantly since while the EN version drifted out of sync. This repository contains the dependent-translation dictionary plus the infrastructure to:

- automatically translate RU → EN changes via EDT LanguageTool,
- fix residual auto-generation bugs (the post-build patcher),
- guard the public API surface against backward-incompatible drift (schema + verifier),
- export ready-to-PR English XML sources back into the main repository.

The goal is not to replace the historical hand translation but to reproduce its style for new components and preserve API stability for existing consumers.

## Layout

```
httpconnector-translations/
├── dictionaries_en/                  # EDT dependent translation project
│   ├── DT-INF/DEPENDENT.PMF          # binds to Parent-Project: HTTPConnector
│   └── src/
│       ├── common_en.dict            # shared dict, non-CamelCase identifiers
│       ├── common-camelcase_en.dict  # CamelCase composite identifiers
│       ├── CommonModules/…           # synonym + .trans/.lstr translations
│       └── DataProcessors/…
├── scripts/                          # pipeline + diagnostic scripts
├── api_schema.json                   # public API contract (42 exports)
├── CLAUDE.md                         # detailed technical documentation
└── POSTBUILD_PATCHER.md              # deep dive into the post-build step
```

## How it works

EDT can't translate 100% of the source correctly because of tokenizer quirks and gaps in its built-in dictionaries. The pipeline closes that gap in three layers:

1. **EDT LanguageTool** does the base translation using `dictionaries_en/`.
2. **post-build patcher** applies a fixed set of residual fixes (wrong platform-function aliases, HTTP-verb literal case-folding, platform-object field name word order, etc.).
3. **API contract check** verifies that the public interface hasn't broken.

Result: an English source tree in `HTTPConnector_translated_project/` (inside EDT) which is then exported to XML for the main repo.

## Pipeline (11 steps)

```
1.  clean RU                                    # EDT rebuilds the Russian project
2.  translate                                   # EDT LanguageTool: RU dict → EN artifacts
3.  cleanup_orphan_modules.py                   # drop directories without .mdo (after dict renames)
3a. check_module_header_drift.py                # year/version drift in module-header docstring
4.  postbuild_patch.py                          # 23 phase-1 + 137 phase-2 fixes
5.  clean translated_project                    # EDT re-reads after postbuild
6.  check_translated2.py                        # residual Cyrillic detector (CODE+DOC)
7.  verify_api.py                               # diff against api_schema.json
8.  get_project_errors (whitelist)              # EDT validation of EN modules
9.  export_configuration_to_xml                 # dump to staging
10. cp staging/. → c:/git/HTTPConnector/src/en/ # replace upstream sources
11. final report                                # diff stat, errors, changed files
```

The pipeline is idempotent — a re-run produces a byte-for-byte identical result.

Steps 1–2, 5, 8–9 happen inside EDT (driven via the [EDT-MCP server](https://github.com/DitriXNew/EDT-MCP) with our [new tools](https://github.com/Dmitriy83/EDT-MCP) `translate_configuration`, `export_configuration_to_xml`, `cleanup_orphan_modules`). Steps 3–4, 6–7, 10 are Python scripts from this repo.

## Requirements

- **EDT 2026.1+** — the only version this pipeline targets and the only version our MCP tool PRs are aimed at. The `dictionaries_en/` dependent project does work on EDT 2025.x via the standard EDT mechanism, but the automation (MCP tools) is not supported on 2025.
- **LanguageTool** — installed separately via **Help → Install New Software** on both 2025.x and 2026.1; not bundled with the EDT base distribution.
- **Java 17** (bundled with EDT — Azul Zulu 17).
- **Python 3.10+** for the pipeline scripts.
- **Git** for working with the upstream HTTPConnector.

Optional: the [EDT-MCP plugin](https://github.com/DitriXNew/EDT-MCP) with the `translate_configuration` / `export_configuration_to_xml` / `run_language_tool` / `convert_to_translation_language` / `import_translations_from_translated_object` / `get_translation_project_info` / `cleanup_orphan_modules` tools — to drive the pipeline from an AI assistant (Claude Code, Cursor, Copilot).

## Quick start

1. Import the source project `HTTPConnector_ru` (fork of https://github.com/vbondarevsky/Connector) and the dependent translation project `dictionaries_en` (this repository) into EDT.
2. Make sure the parent-project name in [DEPENDENT.PMF](dictionaries_en/DT-INF/DEPENDENT.PMF) matches the imported source. Default: `HTTPConnector_ru`.
3. Retarget the path constants at the top of each `scripts/*.py` file to your local checkout (defaults point to the maintainer's machine).
4. Walk through the pipeline as documented in [CLAUDE.md → Translation workflow](CLAUDE.md).

## Scripts

Full reference with parameters in [CLAUDE.md → Tooling](CLAUDE.md). Quick index:

**Pipeline (run after every EDT rebuild):**
- `cleanup_orphan_modules.py` — drop module directories left over by dictionary renames
- `check_module_header_drift.py` — detect drift of literal facts (year, version) in the module-header docstring
- `postbuild_patch.py` — fix residual translation bugs, see [POSTBUILD_PATCHER.md](POSTBUILD_PATCHER.md)
- `check_translated2.py` — residual-Cyrillic detector
- `verify_api.py` — API contract check
- `accept_new_api.py` — append a new exported method to the schema after review

**Analysis:**
- `mine_compound_ids.py` — mine RU→EN compound-identifier mappings from the historical hand translation (line-aligned diff)
- `extract_api_schema.py` — capture the API schema once from the hand-translated EN source
- `analyze.py`, `estimate.py`, `extract_untranslated.py`, `extract_all_untranslated.py` — coverage and gap statistics

**Migration / dictionary hygiene:**
- `migrate.py`, `migrate_b.py` — populate the new dictionary from the old one
- `apply_translations.py`, `apply_camelcase.py`, `apply_small.py` — apply curated translation tables
- `sort_dict.py`, `proper_split.py`, `fix_regions.py`, `fix_case.py`, `fix_camelcase.py`, `fix_str_builtins.py`, `fix_platform_fields.py` — dictionary hygiene and EDT-quirk workarounds

## Related projects

- [vbondarevsky/Connector](https://github.com/vbondarevsky/Connector) — the upstream library (RU)
- [DitriXNew/EDT-MCP](https://github.com/DitriXNew/EDT-MCP) — MCP server for EDT (required for the pipeline tools)
- [Dmitriy83/EDT-MCP](https://github.com/Dmitriy83/EDT-MCP) — fork with the new tools (LanguageTool + Workspace export/import); PRs open against upstream

## License

Matches the [HTTPConnector](https://github.com/vbondarevsky/Connector/blob/master/LICENSE.md) license.
