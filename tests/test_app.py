"""Smoke tests that run the Streamlit UI headlessly."""

import unittest
from datetime import date

try:
    from streamlit.testing.v1 import AppTest
except ImportError:  # pragma: no cover - Streamlit is an install dependency
    AppTest = None


def _today_app() -> None:
    from datetime import date
    from unittest import mock

    from ignire_calendar import app

    with mock.patch.object(app, "local_today", return_value=date(2026, 10, 7)):
        app.main()


@unittest.skipIf(AppTest is None, "Streamlit is not installed")
class StreamlitAppTests(unittest.TestCase):
    def run_app(self) -> "AppTest":
        at = AppTest.from_function(_today_app, default_timeout=30)
        at.run()
        self.assertFalse(at.exception, at.exception)
        return at

    def test_today_card_and_tabs_render(self) -> None:
        at = self.run_app()
        headings = [markdown.value.strip("# ") for markdown in at.markdown]
        self.assertIn("新曆 4 年 2 月 17 日", headings)
        self.assertEqual(len(at.tabs), 4)

    def test_gregorian_to_ignire_form(self) -> None:
        at = self.run_app()
        at.date_input[0].set_value(date(2024, 3, 1))
        at.button[0].click().run()
        self.assertFalse(at.exception)
        self.assertEqual(
            at.success[0].value,
            "2024-03-01（星期五）→ 新曆 1 年 7/12（序日 192）",
        )

    def test_ignire_to_gregorian_form(self) -> None:
        at = self.run_app()
        at.number_input[0].set_value(4)
        at.number_input[1].set_value(2)
        at.number_input[2].set_value(17)
        at.button[1].click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.success[0].value, "新曆 4 年 2/17 → 公曆 2026-10-07（星期三）")

    def test_month_view_highlights_today(self) -> None:
        at = self.run_app()
        grid = next(markdown.value for markdown in at.markdown if "ignire-grid" in markdown.value)
        self.assertEqual(grid.count('class="cell'), 30)
        self.assertEqual(grid.count("cell today"), 1)


if __name__ == "__main__":
    unittest.main()
