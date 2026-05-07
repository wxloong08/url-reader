import unittest
import tempfile
from pathlib import Path

from scripts.saver import save, _determine_referer


class RefererTests(unittest.TestCase):
    def test_xiaohongshu_image_gets_correct_referer(self):
        self.assertEqual(
            _determine_referer("https://sns-webpic-qc.xhscdn.com/img.jpg"),
            "https://www.xiaohongshu.com/",
        )

    def test_wechat_image_gets_correct_referer(self):
        self.assertEqual(
            _determine_referer("https://mmbiz.qpic.cn/sz_mmbiz_png/abc/0"),
            "https://mp.weixin.qq.com/",
        )

    def test_unknown_image_gets_empty_referer(self):
        self.assertEqual(_determine_referer("https://example.com/img.png"), "")


class SaveTests(unittest.TestCase):
    def test_save_creates_content_md_with_front_matter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = save(
                content="# Test Title\n\nBody text here.",
                url="https://example.com/article",
                platform_name="测试平台",
                output_dir=tmpdir,
                verbose=False,
            )

            self.assertTrue(result["success"])
            self.assertEqual(result["title"], "Test Title")
            self.assertEqual(result["images"], 0)

            md_path = Path(result["md_file"])
            self.assertTrue(md_path.exists())

            content = md_path.read_text(encoding="utf-8")
            self.assertIn("title: Test Title", content)
            self.assertIn("platform: 测试平台", content)
            self.assertIn("url: https://example.com/article", content)
            self.assertIn("Body text here.", content)


if __name__ == "__main__":
    unittest.main()
