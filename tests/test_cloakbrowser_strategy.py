import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from scripts.strategies.cloakbrowser_strategy import CloakBrowserStrategy


class CloakBrowserStrategyTests(unittest.TestCase):
    @patch("scripts.strategies.cloakbrowser_strategy.launch_context_async", new_callable=AsyncMock)
    @patch("scripts.strategies.cloakbrowser_strategy.config.CLOAKBROWSER_BINARY_PATH", Path(__file__))
    @patch("scripts.strategies.cloakbrowser_strategy.config.CLOAKBROWSER_ENABLED", True)
    def test_fetch_uses_cloakbrowser_context_and_returns_markdown(self, mock_launch_context):
        page = AsyncMock()
        page.evaluate.return_value = {
            "title": "Example Title",
            "author": "Example Author",
            "publishTime": "2026-05-10",
            "content": (
                "First paragraph with enough text to resemble a real article body.\n"
                "Second paragraph continues the content so the strategy does not treat it as too short."
            ),
        }

        context = AsyncMock()
        context.new_page.return_value = page
        mock_launch_context.return_value = context

        strategy = CloakBrowserStrategy()
        result = strategy.fetch("https://example.com/post", {"id": "generic", "name": "通用网站"})

        self.assertTrue(result["success"])
        self.assertEqual(result["strategy"], "CloakBrowser")
        self.assertIn("First paragraph with enough text", result["content"])
        self.assertEqual(result["metadata"]["title"], "Example Title")
        self.assertEqual(result["metadata"]["author"], "Example Author")
        self.assertEqual(result["metadata"]["publishTime"], "2026-05-10")
        mock_launch_context.assert_awaited()

    def test_fetch_rejects_non_http_url(self):
        strategy = CloakBrowserStrategy()
        result = strategy.fetch("file:///tmp/example.html", {"id": "generic", "name": "通用网站"})
        self.assertFalse(result["success"])
        self.assertIn("不支持", result["error"])


if __name__ == "__main__":
    unittest.main()
