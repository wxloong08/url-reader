import unittest

from scripts.formatter import format_result, format_saved_result


class FormatResultQuietTests(unittest.TestCase):
    def test_quiet_success_returns_content_only(self):
        result = {
            "success": True,
            "strategy": "Firecrawl",
            "platform": {"id": "generic", "name": "通用网站"},
            "content": "# Title\n\nBody text",
        }
        output = format_result(result, "https://example.com", quiet=True)
        self.assertEqual(output, "# Title\n\nBody text")
        self.assertNotIn("**来源**", output)
        self.assertNotIn("**读取策略**", output)
        self.assertNotIn("**原文链接**", output)

    def test_quiet_failure_returns_error_line(self):
        result = {
            "success": False,
            "platform": {"id": "generic", "name": "通用网站"},
            "errors": ["Jina: HTTP 451", "Firecrawl: timeout"],
        }
        output = format_result(result, "https://example.com", quiet=True)
        self.assertEqual(output, "[ERROR] Jina: HTTP 451; Firecrawl: timeout")

    def test_quiet_failure_no_errors_key(self):
        result = {"success": False, "platform": {"id": "generic", "name": "通用网站"}}
        output = format_result(result, "https://example.com", quiet=True)
        self.assertEqual(output, "[ERROR] unknown error")

    def test_non_quiet_success_includes_metadata(self):
        result = {
            "success": True,
            "strategy": "Jina Reader",
            "platform": {"id": "generic", "name": "通用网站"},
            "content": "Body",
        }
        output = format_result(result, "https://example.com", quiet=False)
        self.assertIn("**来源**: 通用网站", output)
        self.assertIn("**读取策略**: Jina Reader", output)
        self.assertIn("**原文链接**: https://example.com", output)


class SavedFormatterTests(unittest.TestCase):
    def test_social_post_save_format_uses_llm_friendly_sections(self):
        result = {
            "success": True,
            "strategy": "Jina Reader",
            "platform": {"id": "x", "name": "X"},
            "metadata": {"content_type": "social_post"},
            "content": """# 基础技术的力量：两个 Linux几十年没改过的内核参数
**作者**: plantegg
**发布时间**: Thu, 16 Apr 2026 04:34:10 GMT

## 图片

![Image 1: Image](img_01.jpg)

## 正文

第一段

第二段
""",
        }

        formatted = format_saved_result(result, "https://x.com/plantegg/status/2044321931944497364")

        self.assertNotIn("**来源**", formatted)
        self.assertNotIn("**读取策略**", formatted)
        self.assertNotIn("**原文链接**", formatted)
        self.assertIn("## Metadata", formatted)
        self.assertIn("- Author: plantegg", formatted)
        self.assertIn("- Published: Thu, 16 Apr 2026 04:34:10 GMT", formatted)
        self.assertIn("## Images", formatted)
        self.assertIn("## Content", formatted)

    def test_forum_save_format_uses_thread_and_reply_sections(self):
        result = {
            "success": True,
            "strategy": "Jina Reader",
            "platform": {"id": "nodeseek", "name": "NodeSeek"},
            "metadata": {"content_type": "forum_thread"},
            "content": """# 测试帖子
**楼主**: tester
**信息**: 1day ago in 技术

## 主楼

这里是主楼正文

## 回复

1. user1 | 1day ago | #1
有人实测过吗

2. user2 | 1day ago | #2
大概 4 天左右 Google 定位恢复了，但是 Gemini 还没解锁
""",
        }

        formatted = format_saved_result(result, "https://www.nodeseek.com/post-123-1")

        self.assertIn("## Metadata", formatted)
        self.assertIn("- Original Poster: tester", formatted)
        self.assertIn("- Context: 1day ago in 技术", formatted)
        self.assertIn("## Thread", formatted)
        self.assertIn("## Replies", formatted)
        self.assertIn("### Reply 1 | user1 | 1day ago | #1", formatted)
        self.assertIn("### Reply 2 | user2 | 1day ago | #2", formatted)
        self.assertNotIn("## 主楼", formatted)
        self.assertNotIn("1. user1 | 1day ago | #1", formatted)


if __name__ == "__main__":
    unittest.main()
