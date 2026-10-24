# changelog-lint

Проверяет `CHANGELOG.md` по правилам [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/): заголовок, `[Unreleased]`, известные разделы, формат версий и дат, порядок релизов и ссылки внизу файла. Офлайн, без зависимостей, Python 3.10+.

## Быстрый старт

Требуется Python 3.10+. Готовый wheel можно скачать в [последнем релизе](https://github.com/GhosTnever-lkm/changelog-lint/releases/latest):

```bash
python -m pip install changelog_lint-0.1.4-py3-none-any.whl
changelog-lint CHANGELOG.md --strict
```

```bash
python -m changelog_lint                 # ./CHANGELOG.md
python -m changelog_lint CHANGELOG.md --strict
python -m changelog_lint CHANGELOG.md --json
```

Пример: [examples/CHANGELOG.md](examples/CHANGELOG.md) — проходит без замечаний.

## Правила

| Код | Уровень | Смысл |
| --- | --- | --- |
| `NO_TITLE` | error | файл не начинается с `# …` |
| `BAD_HEADING` | error | заголовок релиза не `## [версия] - дата` |
| `UNKNOWN_SECTION` | error | раздел не из Added, Changed, Deprecated, Removed, Fixed, Security |
| `BAD_DATE` | error | дата не в формате `YYYY-MM-DD` |
| `FUTURE_DATE` | error | дата позже сегодняшней |
| `ORDER` | error | версии не идут от новых к старым |
| `DUPLICATE_UNRELEASED` | error | больше одного `[Unreleased]` |
| `DUPLICATE_SECTION` | warning | раздел повторяется внутри релиза |
| `NON_SEMVER` | warning | версия не `MAJOR.MINOR.PATCH` |
| `MISSING_DATE` | warning | у релиза нет даты |
| `EMPTY_RELEASE` | warning | релиз без разделов |
| `NO_LINK` | warning | у версии нет ссылки `[версия]: …` внизу |
| `NO_UNRELEASED` | warning | нет раздела `[Unreleased]` |

Коды возврата: `0` — ок, `1` — есть ошибки (или любые замечания при `--strict`), `2` — файл не читается.

## Ограничения

- Проверяет структуру, но не смысл записей и не сверяет версии с git-тегами.
- Дата «сегодня» берётся с локальных часов машины.
- Заголовки и ссылки внутри fenced code blocks игнорируются. Сравнение prerelease-идентификаторов SemVer учитывает числовой порядок (`rc.2` меньше `rc.10`).
- Версии проверяются по SemVer 2.0: пустые идентификаторы и ведущие нули в числовых частях отклоняются; build metadata принимается и не влияет на порядок.

## Разработка

```bash
python -m unittest discover -s tests -t .
```

## Лицензия

MIT — см. [LICENSE](LICENSE).

## История изменений и безопасность

См. [CHANGELOG.md](CHANGELOG.md) и [SECURITY.md](SECURITY.md).

## Использование в CI

```yaml
- uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
- uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
  with:
    python-version: "3.12"
- name: changelog-lint
  run: python -m changelog_lint CHANGELOG.md --strict
```
