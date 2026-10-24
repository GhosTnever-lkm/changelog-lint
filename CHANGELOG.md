# Changelog

Все заметные изменения проекта документируются в этом файле.
Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/).

## [Unreleased]

### Fixed

- Update the README wheel installation example to the current package version and test that it stays in sync.

## [0.1.4] - 2026-10-25

### Fixed

- Validate release versions against SemVer 2.0, including numeric leading-zero and empty-identifier rules.
- Accept build metadata and ignore it when checking release precedence.

## [0.1.3] - 2026-10-13

### Fixed

- Compare SemVer prerelease identifiers correctly, including numeric identifiers.
- Ignore release headings and link definitions inside fenced Markdown examples.
- Add installable wheel and source distributions to tagged GitHub releases.

## [0.1.2] - 2026-10-11

### Added

- CI now also runs the test suite on Windows (windows-latest), not only Ubuntu.

## [0.1.1] - 2026-10-11

### Added

- Этот файл CHANGELOG.md: проект теперь проходит собственную проверку (раньше README ссылался на отсутствующий файл).

## [0.1.0] - 2026-10-10

### Added

- Проверка CHANGELOG.md по правилам Keep a Changelog: заголовок, `[Unreleased]`, разделы, формат версий и дат, порядок релизов, ссылки внизу файла.
- CLI с флагами `--strict` и `--json`, коды возврата для CI.
- Пример [examples/CHANGELOG.md](examples/CHANGELOG.md), тесты и workflow CI.
- CONTRIBUTING.md и SECURITY.md.

[0.1.2]: https://github.com/GhosTnever-lkm/changelog-lint/compare/v0.1.1...v0.1.2
[0.1.3]: https://github.com/GhosTnever-lkm/changelog-lint/releases/tag/v0.1.3
[0.1.4]: https://github.com/GhosTnever-lkm/changelog-lint/compare/v0.1.3...v0.1.4
[0.1.1]: https://github.com/GhosTnever-lkm/changelog-lint/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/GhosTnever-lkm/changelog-lint/releases/tag/v0.1.0
