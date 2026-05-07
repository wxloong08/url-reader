import unittest
from unittest.mock import patch, MagicMock

from scripts.strategies.jina import JinaStrategy, _is_blocked_page


class JinaBlockedPageTests(unittest.TestCase):
    def test_detects_blocked_page(self):
        self.assertTrue(_is_blocked_page("You've been blocked by network security"))
        self.assertTrue(_is_blocked_page("Access Denied - please verify"))
        self.assertTrue(_is_blocked_page("please prove you are not a bot"))

    def test_passes_normal_content(self):
        self.assertFalse(_is_blocked_page("# Hello World\n\nThis is a normal article."))
        self.assertFalse(_is_blocked_page(""))


class JinaStrategyTests(unittest.TestCase):
    @patch("scripts.strategies.jina.requests.get")
    def test_fetch_returns_content_on_200(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "Title: Test\n\nMarkdown Content:\n\n# Hello\n\nThis is content that is long enough to pass the length check easily."
        mock_get.return_value = mock_resp

        strategy = JinaStrategy()
        result = strategy.fetch("https://example.com", {"id": "generic"})

        self.assertTrue(result["success"])
        self.assertIn("Hello", result["content"])

    @patch("scripts.strategies.jina.requests.get")
    def test_fetch_fails_on_451(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 451
        mock_get.return_value = mock_resp

        strategy = JinaStrategy()
        result = strategy.fetch("https://example.com", {"id": "generic"})

        self.assertFalse(result["success"])
        self.assertIn("451", result["error"])

    @patch("scripts.strategies.jina.requests.get")
    def test_fetch_rejects_short_content(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "short"
        mock_get.return_value = mock_resp

        strategy = JinaStrategy()
        result = strategy.fetch("https://example.com", {"id": "generic"})

        self.assertFalse(result["success"])
        self.assertIn("太短", result["error"])

    @patch("scripts.strategies.jina.requests.get")
    def test_fetch_rejects_blocked_page(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "You've been blocked by network security. Please verify you are human. " + "x" * 200
        mock_get.return_value = mock_resp

        strategy = JinaStrategy()
        result = strategy.fetch("https://example.com", {"id": "generic"})

        self.assertFalse(result["success"])
        self.assertIn("屏蔽", result["error"])


if __name__ == "__main__":
    unittest.main()
