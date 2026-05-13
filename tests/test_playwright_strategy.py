import unittest
from unittest.mock import AsyncMock

from scripts.strategies.playwright_strategy import PlaywrightStrategy


class PlaywrightFinanceStockTests(unittest.IsolatedAsyncioTestCase):
    def test_navigation_timeout_is_shorter_for_finance_stock(self):
        strategy = PlaywrightStrategy()

        self.assertEqual(strategy._get_navigation_timeout({"cleanup_profile": "finance_stock"}), 15000)
        self.assertEqual(strategy._get_navigation_timeout({"cleanup_profile": "generic"}), 30000)

    async def test_wait_for_page_ready_prefers_table_for_finance_stock(self):
        strategy = PlaywrightStrategy()
        page = AsyncMock()

        await strategy._wait_for_page_ready(page, {"cleanup_profile": "finance_stock"})

        page.wait_for_selector.assert_awaited_with("table", timeout=15000)


if __name__ == "__main__":
    unittest.main()
