import contextlib
import io
import tempfile
import unittest
from datetime import date
from pathlib import Path

from changelog_lint import __version__
from changelog_lint.cli import main
from changelog_lint.core import lint

TODAY = date(2026, 10, 11)
GOOD = Path("examples/CHANGELOG.md").read_text(encoding="utf-8")


def codes(text):
    return {f.code for f in lint(text, today=TODAY)}


class RuleTests(unittest.TestCase):
    def test_example_is_clean(self):
        self.assertEqual(lint(GOOD, today=TODAY), [])

    def test_missing_title(self):
        self.assertIn("NO_TITLE", codes("## [Unreleased]\n"))

    def test_unknown_section(self):
        text = "# C\n\n## [Unreleased]\n\n### Improved\n\n- x\n"
        self.assertIn("UNKNOWN_SECTION", codes(text))

    def test_bad_heading(self):
        self.assertIn("BAD_HEADING", codes("# C\n\n## Version one\n"))

    def test_future_and_bad_dates(self):
        self.assertIn("FUTURE_DATE", codes("# C\n\n## [1.0.0] - 2030-01-01\n\n### Added\n\n- x\n"))
        self.assertIn("BAD_DATE", codes("# C\n\n## [1.0.0] - 01/02/2026\n\n### Added\n\n- x\n"))

    def test_order_violation(self):
        text = "# C\n\n## [1.0.0] - 2026-01-01\n\n### Added\n\n- a\n\n## [2.0.0] - 2026-02-01\n\n### Added\n\n- b\n"
        self.assertIn("ORDER", codes(text))

    def test_semver_prerelease_sorts_before_stable_release(self):
        text = "# C\n\n## [Unreleased]\n\n## [1.0.0] - 2026-01-02\n\n### Added\n\n- stable\n\n## [1.0.0-rc.1] - 2026-01-01\n\n### Added\n\n- candidate\n"
        self.assertNotIn("ORDER", codes(text))

    def test_numeric_prerelease_identifiers_are_compared_numerically(self):
        text = "# C\n\n## [Unreleased]\n\n## [1.0.0-rc.2] - 2026-01-02\n\n### Added\n\n- two\n\n## [1.0.0-rc.10] - 2026-01-01\n\n### Added\n\n- ten\n"
        self.assertIn("ORDER", codes(text))

    def test_invalid_semver_identifiers_warn(self):
        for version in ("01.0.0", "1.0.0-01", "1.0.0-alpha..beta", "1.0.0-alpha."):
            with self.subTest(version=version):
                text = f"# C\n\n## [Unreleased]\n\n## [{version}] - 2026-01-01\n\n### Added\n\n- item\n"
                self.assertIn("NON_SEMVER", codes(text))

    def test_build_metadata_is_valid_and_does_not_change_precedence(self):
        text = "# C\n\n## [Unreleased]\n\n## [1.0.0+build.2] - 2026-01-02\n\n### Added\n\n- newer\n\n## [1.0.0+build.1] - 2026-01-01\n\n### Added\n\n- same precedence\n"
        issue_codes = codes(text)
        self.assertNotIn("NON_SEMVER", issue_codes)
        self.assertIn("ORDER", issue_codes)

    def test_release_headings_inside_fenced_examples_are_ignored(self):
        text = "# C\n\n## [Unreleased]\n\n## [1.0.0] - 2026-01-01\n\n### Added\n\n- example\n\n````markdown\n## [9.9.9] - 2099-01-01\n\n### Improved\n```\n````\n\n[1.0.0]: https://example.invalid\n"
        issue_codes = codes(text)
        self.assertNotIn("FUTURE_DATE", issue_codes)
        self.assertNotIn("ORDER", issue_codes)
        self.assertNotIn("UNKNOWN_SECTION", issue_codes)
        self.assertNotIn("NO_LINK", issue_codes)

    def test_duplicate_unreleased(self):
        text = "# C\n\n## [Unreleased]\n\n## [Unreleased]\n"
        self.assertIn("DUPLICATE_UNRELEASED", codes(text))

    def test_missing_link_and_empty_release_warn(self):
        text = "# C\n\n## [Unreleased]\n\n## [1.0.0] - 2026-01-01\n"
        c = codes(text)
        self.assertIn("EMPTY_RELEASE", c)
        self.assertIn("NO_LINK", c)

    def test_non_semver_warns(self):
        text = "# C\n\n## [Unreleased]\n\n## [v1] - 2026-01-01\n\n### Added\n\n- x\n"
        self.assertIn("NON_SEMVER", codes(text))


class CliTests(unittest.TestCase):
    def run_cli(self, argv):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = main(argv)
        return code, buf.getvalue()

    def test_good_exit_zero(self):
        code, out = self.run_cli(["examples/CHANGELOG.md"])
        self.assertEqual(code, 0)
        self.assertIn("OK", out)

    def test_readme_wheel_command_matches_package_version(self):
        readme = Path("README.md").read_text(encoding="utf-8")
        expected = f"python -m pip install changelog_lint-{__version__}-py3-none-any.whl"
        self.assertIn(expected, readme)

    def test_readme_action_pins_match_workflows(self):
        readme = Path("README.md").read_text(encoding="utf-8")
        for action in ("actions/checkout@", "actions/setup-python@"):
            documented = next(line.strip() for line in readme.splitlines() if line.strip().startswith("- uses: " + action))
            for workflow in (".github/workflows/ci.yml", ".github/workflows/release.yml"):
                configured = next(line.strip() for line in Path(workflow).read_text(encoding="utf-8").splitlines() if line.strip().startswith("- uses: " + action))
                self.assertEqual(documented.removeprefix("- "), configured.removeprefix("- "), workflow)

    def test_error_exit_one_and_missing_file_two(self):
        tmp = Path(tempfile.mkdtemp()) / "CHANGELOG.md"
        tmp.write_text("# C\n\n## Random\n", encoding="utf-8")
        self.assertEqual(self.run_cli([str(tmp)])[0], 1)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.run_cli(["/no/CHANGELOG.md"])[0], 2)


if __name__ == "__main__":
    unittest.main()
