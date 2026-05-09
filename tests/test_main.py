import unittest

from scripts.main import _prepare_content_for_postprocess


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


if __name__ == "__main__":
    unittest.main()
