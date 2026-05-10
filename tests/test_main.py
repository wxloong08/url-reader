import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

from scripts.main import _filter_available_strategies, _prepare_content_for_postprocess


class MainPreparationTests(unittest.TestCase):
    def test_prepare_content_wraps_strategy_metadata_for_postprocess(self):
        content = "Body paragraph"
        metadata = {
            "title": "Example Title | Reuters",
            "source_url": "https://www.reuters.com/example",
            "published_time": "Fri, 08 May 2026 00:00:00 GMT",
        }

        prepared = _prepare_content_for_postprocess(content, metadata, "https://www.reuters.com/example")

        self.assertIn("Title: Example Title | Reuters", prepared)
        self.assertIn("URL Source: https://www.reuters.com/example", prepared)
        self.assertIn("Published Time: Fri, 08 May 2026 00:00:00 GMT", prepared)
        self.assertIn("Markdown Content:\n\nBody paragraph", prepared)

    def test_prepare_content_keeps_existing_wrapped_content_unchanged(self):
        content = "Title: Existing\n\nURL Source: https://example.com\n\nMarkdown Content:\nBody"
        metadata = {"title": "Ignored"}

        prepared = _prepare_content_for_postprocess(content, metadata, "https://example.com")

        self.assertEqual(prepared, content)

    @patch("scripts.main.config.CLOAKBROWSER_ENABLED", False)
    def test_filter_available_strategies_skips_cloakbrowser_when_disabled(self):
        filtered = _filter_available_strategies(["cloakbrowser", "opencli_browser"])
        self.assertEqual(filtered, ["opencli_browser"])

    @patch.dict("sys.modules", {"cloakbrowser": ModuleType("cloakbrowser")})
    @patch("scripts.main.config.CLOAKBROWSER_BINARY_PATH", Path(__file__))
    @patch("scripts.main.config.CLOAKBROWSER_ENABLED", True)
    def test_filter_available_strategies_keeps_cloakbrowser_when_enabled_and_binary_exists(self):
        filtered = _filter_available_strategies(["cloakbrowser", "opencli_browser"])
        self.assertEqual(filtered, ["cloakbrowser", "opencli_browser"])

    @patch("scripts.main.config.CLOAKBROWSER_BINARY_PATH", None)
    @patch("scripts.main.config.CLOAKBROWSER_ENABLED", True)
    def test_filter_available_strategies_skips_cloakbrowser_when_binary_path_missing(self):
        filtered = _filter_available_strategies(["cloakbrowser", "opencli_browser"])
        self.assertEqual(filtered, ["opencli_browser"])


if __name__ == "__main__":
    unittest.main()
