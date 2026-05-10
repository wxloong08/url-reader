"""CloakBrowser fetch strategy — optional stealth browser fallback."""

import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from scripts import config
from scripts.content import detect_verification_page
from scripts.strategies import FetchStrategy

try:
    from cloakbrowser import launch_context_async  # type: ignore
except ImportError:
    launch_context_async = None


class CloakBrowserStrategy(FetchStrategy):

    name = "CloakBrowser"

    def fetch(self, url: str, platform: dict) -> dict:
        if not url.startswith(("http://", "https://")):
            return {'success': False, 'error': 'CloakBrowser 不支持非 HTTP(S) URL'}

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop is not None:
            with ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(asyncio.run, self._fetch_async(url, platform)).result()
        return asyncio.run(self._fetch_async(url, platform))

    async def _fetch_async(self, url: str, platform: dict) -> dict:
        if launch_context_async is None:
            return {'success': False, 'error': 'cloakbrowser 未安装'}

        if not config.CLOAKBROWSER_ENABLED:
            return {'success': False, 'error': 'CloakBrowser 未启用'}

        if not config.CLOAKBROWSER_BINARY_PATH or not config.CLOAKBROWSER_BINARY_PATH.exists():
            return {'success': False, 'error': 'CloakBrowser 二进制路径不存在'}

        context = None
        try:
            self._prepare_environment()
            context = await launch_context_async(
                headless=config.HEADLESS,
                backend=config.CLOAKBROWSER_BACKEND,
            )
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=config.TIMEOUT * 1000)
            await page.wait_for_timeout(1500)
            payload = await self._extract_generic(page)
            content = (payload.get('content') or '').strip()

            if detect_verification_page(content):
                return {'success': False, 'error': '页面需要验证'}

            if len(content) < 100:
                return {'success': False, 'error': '页面内容提取失败'}

            return {
                'success': True,
                'strategy': self.name,
                'content': content,
                'metadata': {
                    'title': payload.get('title', ''),
                    'author': payload.get('author', ''),
                    'publishTime': payload.get('publishTime', ''),
                    'source_url': url,
                },
            }
        except Exception as e:
            return {'success': False, 'error': f'CloakBrowser 错误: {e}'}
        finally:
            if context is not None:
                try:
                    await context.close()
                except Exception:
                    pass

    @staticmethod
    def _prepare_environment() -> None:
        os.environ["CLOAKBROWSER_BINARY_PATH"] = str(config.CLOAKBROWSER_BINARY_PATH)
        os.environ["CLOAKBROWSER_AUTO_UPDATE"] = "false"
        os.environ["CLOAKBROWSER_SKIP_CHECKSUM"] = "false"
        os.environ["CLOAKBROWSER_BACKEND"] = str(config.CLOAKBROWSER_BACKEND or "playwright")

    @staticmethod
    async def _extract_generic(page) -> dict:
        return await page.evaluate("""
            () => {
                const title = document.querySelector('h1')?.innerText?.trim()
                    || document.querySelector('title')?.innerText?.trim()
                    || '';
                const author = document.querySelector('meta[name="author"]')?.content?.trim() || '';
                const publishTime = document.querySelector('time')?.innerText?.trim() || '';
                const content = document.body?.innerText?.trim() || '';
                return { title, author, publishTime, content };
            }
        """)
