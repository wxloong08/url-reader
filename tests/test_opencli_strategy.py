import json
import unittest
from unittest.mock import MagicMock, patch

from scripts.strategies.opencli_browser import OpenCLIBrowserStrategy


class OpenCLIBrowserStrategyTests(unittest.TestCase):
    @patch("scripts.strategies.opencli_browser.shutil.which", return_value="opencli")
    @patch("scripts.strategies.opencli_browser.subprocess.run")
    def test_fetch_uses_open_extract_and_returns_markdown_content(self, mock_run, _mock_which):
        open_result = MagicMock()
        open_result.returncode = 0
        open_result.stdout = json.dumps({"url": "https://www.zhihu.com/question/10434775822", "page": "TAB123"})
        open_result.stderr = ""

        extract_result = MagicMock()
        extract_result.returncode = 0
        extract_result.stdout = json.dumps({
            "url": "https://www.zhihu.com/question/10434775822",
            "title": "claude怎么订阅最便宜？ - 知乎",
            "content": "# claude怎么订阅最便宜？\n\n#### 2 个回答\n\n[麻小辣](//www.zhihu.com/people/a)\n\n回答正文",
        })
        extract_result.stderr = ""

        close_result = MagicMock()
        close_result.returncode = 0
        close_result.stdout = ""
        close_result.stderr = ""

        mock_run.side_effect = [open_result, extract_result, close_result]

        strategy = OpenCLIBrowserStrategy()
        result = strategy.fetch("https://www.zhihu.com/question/10434775822", {"id": "zhihu", "name": "知乎"})

        self.assertTrue(result["success"])
        self.assertEqual(result["strategy"], "OpenCLI Browser")
        self.assertIn("claude怎么订阅最便宜？", result["content"])
        self.assertEqual(mock_run.call_args_list[1].args[0][:4], ["opencli", "browser", "extract", "--tab"])

    @patch("scripts.strategies.opencli_browser.shutil.which", return_value="opencli")
    @patch("scripts.strategies.opencli_browser.subprocess.run")
    def test_fetch_retries_without_selector_when_main_selector_fails(self, mock_run, _mock_which):
        open_result = MagicMock(returncode=0, stdout=json.dumps({"page": "TAB123"}), stderr="")
        selector_fail = MagicMock(
            returncode=1,
            stdout="",
            stderr=json.dumps({"error": {"code": "selector_not_found", "message": "Selector \"main\" matched 0 elements."}}),
        )
        extract_result = MagicMock(
            returncode=0,
            stdout=json.dumps({"title": "Example", "content": "example body"}),
            stderr="",
        )
        close_result = MagicMock(returncode=0, stdout="", stderr="")
        mock_run.side_effect = [open_result, selector_fail, extract_result, close_result]

        strategy = OpenCLIBrowserStrategy()
        result = strategy.fetch("https://www.reddit.com/r/OpenAI/comments/abc123/example/", {"id": "reddit", "name": "Reddit"})

        self.assertTrue(result["success"])
        self.assertEqual(mock_run.call_args_list[1].args[0], ["opencli", "browser", "extract", "--tab", "TAB123", "--selector", "main"])
        self.assertEqual(mock_run.call_args_list[2].args[0], ["opencli", "browser", "extract", "--tab", "TAB123"])


if __name__ == "__main__":
    unittest.main()
