import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

from scripts.main import _filter_available_strategies, _prepare_content_for_postprocess, _truncate, read_url


class TruncateTests(unittest.TestCase):
    def test_disabled_when_zero(self):
        self.assertEqual(_truncate("hello world", 0), "hello world")

    def test_no_truncation_when_within_limit(self):
        self.assertEqual(_truncate("short", 100), "short")

    def test_empty_string(self):
        self.assertEqual(_truncate("", 100), "")

    def test_cuts_at_line_boundary_when_close(self):
        text = "aaaa\nbbbb\ncccc"
        result = _truncate(text, 8)
        self.assertTrue(result.startswith("aaaa\n"))
        self.assertIn("[...truncated,", result)

    def test_cuts_at_max_when_line_boundary_too_far(self):
        text = "a" * 100 + "\n" + "b" * 50
        result = _truncate(text, 50)
        self.assertIn("50/151 chars shown", result)

    def test_marker_shows_correct_counts(self):
        text = "line1\nline2\nline3\nline4"
        result = _truncate(text, 12)
        self.assertIn("[...truncated,", result)
        self.assertIn(f"/{len(text)} chars shown", result)


class FakeStrategy:
    def __init__(self, name: str, result: dict, calls: list[str]):
        self.name = name
        self.result = result
        self.calls = calls

    def fetch(self, url: str, platform: dict) -> dict:
        self.calls.append(self.name)
        return self.result


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

    @patch("scripts.main.postprocess_content")
    @patch("scripts.main._filter_available_strategies")
    @patch("scripts.main.identify_platform")
    def test_read_url_inserts_opencli_after_login_or_verification_failure(
        self,
        mock_identify_platform,
        mock_filter_available_strategies,
        mock_postprocess_content,
    ):
        calls: list[str] = []
        platform = {
            "id": "generic",
            "name": "通用网站",
            "preferred_strategies": ["jina", "playwright"],
            "cleanup_profile": "generic",
        }
        mock_identify_platform.return_value = platform
        mock_filter_available_strategies.return_value = ["jina", "playwright"]
        mock_postprocess_content.return_value = {
            "success": True,
            "content": "# OpenCLI content",
            "metadata": {"content_type": "article"},
        }

        strategies = {
            "jina": FakeStrategy("Jina Reader", {"success": False, "error": "页面需要验证"}, calls),
            "opencli_browser": FakeStrategy(
                "OpenCLI Browser",
                {"success": True, "strategy": "OpenCLI Browser", "content": "OpenCLI raw content", "metadata": {"title": "OpenCLI"}},
                calls,
            ),
            "playwright": FakeStrategy(
                "Playwright",
                {"success": True, "strategy": "Playwright", "content": "Playwright raw content", "metadata": {"title": "Playwright"}},
                calls,
            ),
        }

        with patch("scripts.main._STRATEGIES", strategies):
            result = read_url("https://example.com/login-gated", verbose=False)

        self.assertTrue(result["success"])
        self.assertEqual(calls, ["Jina Reader", "OpenCLI Browser"])
        self.assertEqual(result["strategy"], "OpenCLI Browser")
        self.assertEqual(result["content"], "# OpenCLI content")

    @patch("scripts.main.postprocess_content")
    @patch("scripts.main._filter_available_strategies")
    @patch("scripts.main.identify_platform")
    def test_read_url_does_not_try_opencli_twice_when_already_in_strategy_chain(
        self,
        mock_identify_platform,
        mock_filter_available_strategies,
        mock_postprocess_content,
    ):
        calls: list[str] = []
        platform = {
            "id": "generic",
            "name": "通用网站",
            "preferred_strategies": ["jina", "opencli_browser", "playwright"],
            "cleanup_profile": "generic",
        }
        mock_identify_platform.return_value = platform
        mock_filter_available_strategies.return_value = ["jina", "opencli_browser", "playwright"]
        mock_postprocess_content.return_value = {
            "success": True,
            "content": "# Playwright content",
            "metadata": {"content_type": "article"},
        }

        strategies = {
            "jina": FakeStrategy("Jina Reader", {"success": False, "error": "页面需要验证"}, calls),
            "opencli_browser": FakeStrategy("OpenCLI Browser", {"success": False, "error": "opencli 提取内容过短"}, calls),
            "playwright": FakeStrategy(
                "Playwright",
                {"success": True, "strategy": "Playwright", "content": "Playwright raw content", "metadata": {"title": "Playwright"}},
                calls,
            ),
        }

        with patch("scripts.main._STRATEGIES", strategies):
            result = read_url("https://example.com/login-gated", verbose=False)

        self.assertTrue(result["success"])
        self.assertEqual(calls, ["Jina Reader", "OpenCLI Browser", "Playwright"])
        self.assertEqual(result["strategy"], "Playwright")


if __name__ == "__main__":
    unittest.main()
