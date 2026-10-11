import contextlib
import io
import tempfile
import unittest
from datetime import date
from pathlib import Path

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

    def test_error_exit_one_and_missing_file_two(self):
        tmp = Path(tempfile.mkdtemp()) / "CHANGELOG.md"
        tmp.write_text("# C\n\n## Random\n", encoding="utf-8")
        self.assertEqual(self.run_cli([str(tmp)])[0], 1)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.run_cli(["/no/CHANGELOG.md"])[0], 2)


if __name__ == "__main__":
    unittest.main()
