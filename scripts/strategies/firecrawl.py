"""Firecrawl fetch strategy."""

from scripts.strategies import FetchStrategy
from scripts import config
from scripts.content import detect_verification_page


class FirecrawlStrategy(FetchStrategy):

    name = "Firecrawl"

    def fetch(self, url: str, platform: dict) -> dict:
        api_key = config.FIRECRAWL_API_KEY
        if not api_key:
            return {'success': False, 'error': 'FIRECRAWL_API_KEY 未设置'}

        try:
            from firecrawl import Firecrawl
            app = Firecrawl(api_key=api_key)
            result = app.scrape(url)

            if result:
                markdown = getattr(result, 'markdown', '') or ''
                metadata = getattr(result, 'metadata', None)
                if metadata:
                    metadata = metadata.model_dump() if hasattr(metadata, 'model_dump') else {}
                else:
                    metadata = {}

                if markdown and len(markdown) > 100:
                    if detect_verification_page(markdown):
                        return {'success': False, 'error': '页面需要验证'}

                    return {
                        'success': True,
                        'strategy': self.name,
                        'content': markdown,
                        'metadata': metadata,
                    }

            return {'success': False, 'error': 'Firecrawl 返回内容为空'}

        except Exception as e:
            return {'success': False, 'error': f'Firecrawl 错误: {e}'}
