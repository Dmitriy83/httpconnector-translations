# HTTPConnector Translations

Pipeline для поддержки английского перевода библиотеки [HTTPConnector](https://github.com/vbondarevsky/Connector) на актуальном уровне с русским источником. Использует встроенный механизм EDT LanguageTool («зависимый проект перевода») плюс набор скриптов, которые закрывают пробелы автогенерации.

> **Язык документации**: README на русском — основная версия. Английская версия: [README.en.md](README.en.md).

## О проекте

Оригинальная библиотека HTTPConnector развивается на русском языке. Английский перевод изначально был сделан вручную в коммите #79 (2021), но с тех пор RU-источник существенно изменился, а EN-версия отставала. Этот репозиторий — словарь зависимого перевода + инфраструктура, которая позволяет:

- автоматически переводить изменения RU → EN (через EDT LanguageTool),
- править остаточные ошибки автогенерации (post-build patcher),
- следить за обратной совместимостью публичного API (схема + verify-скрипт),
- выгружать готовый английский XML-исходник для PR в основную репу.

Цель — не заменить исторический ручной перевод, а воспроизвести его стиль для всех новых компонентов и поддерживать стабильность контракта API для существующих потребителей.

## Структура

```
httpconnector-translations/
├── dictionaries_en/                  # зависимый проект перевода EDT
│   ├── DT-INF/DEPENDENT.PMF          # привязка к Parent-Project: HTTPConnector
│   └── src/
│       ├── common_en.dict            # общий словарь, не-CamelCase идентификаторы
│       ├── common-camelcase_en.dict  # CamelCase composite identifiers
│       ├── CommonModules/…           # переводы синонимов и .trans/.lstr
│       └── DataProcessors/…
├── scripts/                          # pipeline и диагностические скрипты
│   ├── pipeline/                     #   запускаются на каждой пересборке
│   ├── analysis/                     #   диагностика / одноразовый анализ
│   └── migration/                    #   bootstrap + гигиена словарей
├── api_schema.json                   # контракт публичного API (42 экспорта)
├── CLAUDE.md                         # детальная техническая документация
└── POSTBUILD_PATCHER.md              # глубокое описание post-build шага
```

## Как это работает

EDT не справляется с переводом 100% символов из-за особенностей токенизатора и неполноты внутренних словарей. Pipeline закрывает разрыв в три захода:

1. **EDT LanguageTool** делает базовый перевод используя `dictionaries_en/`.
2. **post-build patcher** правит фиксированный набор остаточных багов перевода (неправильные алиасы платформенных функций, регистр HTTP-методов в литералах, поля платформенных объектов с обратным порядком слов и др.).
3. **API contract check** валидирует что публичный интерфейс библиотеки не сломан.

Результат — английский исходник в `HTTPConnector_translated_project/` (под EDT) и далее экспортируемый в XML для основной репы.

## Pipeline (11 шагов)

```
1.  clean RU                                    # EDT перестраивает русский проект
2.  translate                                   # EDT LanguageTool: RU словарь → EN артефакты
3.  cleanup_orphan_modules.py                   # удаление папок без .mdo (после переименований словаря)
3a. check_module_header_drift.py                # дрейф year/version в module-header
4.  postbuild_patch.py                          # 23 phase-1 + 137 phase-2 правок
5.  clean translated_project                    # EDT перечитывает после postbuild
6.  check_translated.py                        # ищет остаточную кириллицу (CODE+DOC)
7.  verify_api.py                               # сверяет API с api_schema.json
8.  get_project_errors (whitelist)              # EDT-валидация EN-модулей
9.  export_configuration_to_xml                 # выгрузка в staging
10. cp staging/. → c:/git/HTTPConnector/src/en/ # замена
11. финальный отчёт                             # diff stat, ошибки, изменённые файлы
```

Pipeline идемпотентный: повторный прогон даёт байт-в-байт тот же результат.

Шаги 1–2, 5, 8–9 — действия в EDT (через [EDT-MCP сервер](https://github.com/DitriXNew/EDT-MCP) с нашими [новыми тулами](https://github.com/Dmitriy83/EDT-MCP) `translate_configuration`, `export_configuration_to_xml`, `cleanup_orphan_modules`). Шаги 3–4, 6–7, 10 — Python-скрипты из этой репы.

## Требования

- **EDT 2026.1+** — единственная версия, под которую затачивается pipeline и в которую отправляются PR с MCP-тулами. На EDT 2025.x словарь словарей (`dictionaries_en/`) тоже работает через стандартный механизм EDT, но автоматизация (MCP-тулы) для 2025 не поддерживается.
- **LanguageTool** — устанавливается отдельно через **Help → Install New Software** (как на 2025.x, так и на 2026.1 не входит в базовую поставку EDT).
- **Java 17** (поставляется с EDT — Azul Zulu 17).
- **Python 3.10+** для pipeline-скриптов.
- **Git** для работы с upstream HTTPConnector.

Опционально: [EDT-MCP плагин](https://github.com/DitriXNew/EDT-MCP) с тулами `translate_configuration` / `export_configuration_to_xml` / `generate_translation_strings` / `convert_to_translation_language` / `import_translations_from_translated_object` / `get_translation_project_info` / `cleanup_orphan_modules` — для запуска pipeline через AI-ассистент (Claude Code, Cursor, Copilot).

## Быстрый старт

1. Импортировать в EDT основной проект `HTTPConnector_ru` (форк https://github.com/vbondarevsky/Connector) и зависимый проект перевода `dictionaries_en` (этот репозиторий).
2. Имя проекта-родителя в [DEPENDENT.PMF](dictionaries_en/DT-INF/DEPENDENT.PMF) должно совпадать с именем импортированного источника. По умолчанию — `HTTPConnector_ru`.
3. Настроить пути в скриптах под свою машину — отредактировать константы `PROJ` / `MOD` в начале каждого `scripts/<group>/*.py` (по умолчанию они указывают на пути разработчика).
4. Прогнать pipeline шаг за шагом по [CLAUDE.md → Translation workflow](CLAUDE.md).

## Скрипты

Полный обзор и параметры каждого — в [CLAUDE.md → Tooling](CLAUDE.md). Краткий перечень:

**Pipeline (запускаются после каждой пересборки EDT):**
- `cleanup_orphan_modules.py` — удаление мусорных папок модулей после переименований словаря
- `check_module_header_drift.py` — детектор дрейфа литералов (год/версия) в module-header docstring
- `postbuild_patch.py` — фикс остаточных багов перевода, см. [POSTBUILD_PATCHER.md](POSTBUILD_PATCHER.md)
- `check_translated.py` — детектор остаточной кириллицы
- `verify_api.py` — проверка контракта API
- `accept_new_api.py` — пополнение схемы API когда upstream добавляет экспортный метод

**Анализ:**
- `mine_compound_ids.py` — добывает RU→EN маппинги композитных идентификаторов из старого ручного перевода (line-aligned diff)
- `extract_api_schema.py` — снимает API-схему один раз с ручной EN-версии
- `analyze.py`, `estimate.py`, `extract_untranslated.py`, `extract_all_untranslated.py` — статистика покрытия и пробелов

**Миграция / гигиена словарей:**
- `migrate.py`, `migrate_b.py` — заполнение нового словаря из старого
- `apply_translations.py`, `apply_camelcase.py`, `apply_small.py` — применение наработанных таблиц переводов
- `sort_dict.py`, `proper_split.py`, `fix_regions.py`, `fix_case.py`, `fix_camelcase.py`, `fix_str_builtins.py`, `fix_platform_fields.py` — гигиена словарей и обходы EDT-quirk'ов

## Связанные проекты

- [vbondarevsky/Connector](https://github.com/vbondarevsky/Connector) — исходник библиотеки (RU)
- [DitriXNew/EDT-MCP](https://github.com/DitriXNew/EDT-MCP) — MCP-сервер для EDT (нужен для тулов pipeline)
- [Dmitriy83/EDT-MCP](https://github.com/Dmitriy83/EDT-MCP) — fork с новыми тулами (LanguageTool + Workspace export/import) — PR'ы открыты в upstream

## Лицензия

Соответствует лицензии [HTTPConnector](https://github.com/vbondarevsky/Connector/blob/master/LICENSE.md).
