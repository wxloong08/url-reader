"""Chrome CLI browser-extract fetch strategy.

Replaces OpenCLIBrowserStrategy — calls chrome_cli.py directly via daemon HTTP,
no subprocess, no opencli dependency.
"""

import json
import os
import sys
import urllib.request

from scripts.strategies import FetchStrategy

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "chrome-cli")))
import chrome_cli  # noqa: E402


class ChromeCLIStrategy(FetchStrategy):

    name = "Chrome CLI"
    session = "cc-reader"

    def fetch(self, url: str, platform: dict) -> dict:
        if not url.startswith(("http://", "https://")):
            return {"success": False, "error": f"不支持的 URL scheme: {url[:20]}"}

        try:
            req = urllib.request.Request(
                f"{chrome_cli.DAEMON_URL}/status",
                headers={"X-OpenCLI": "1"},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                json.loads(resp.read())
        except Exception as e:
            return {"success": False, "error": f"daemon 连接失败: {e}"}

        page_id = ""
        try:
            nav = chrome_cli.send_command("navigate", url=url, session=self.session)
            page_id = nav.get("page", "")
            if not page_id:
                return {"success": False, "error": "未返回页面标识"}

            import time
            time.sleep(2)

            is_wechat = platform.get("id") == "wechat"
            if is_wechat:
                content_data = self._extract_wechat(page_id)
            else:
                content_data = self._extract(page_id, "main")
                if not content_data:
                    content_data = self._extract(page_id, None)

            if not content_data:
                return {"success": False, "error": "内容提取失败"}

            content = content_data.get("content", "").strip()
            if not content:
                return {"success": False, "error": "页面内容为空"}

            title = content_data.get("title", "")
            source_url = content_data.get("url", url) or url

            wrapped = (
                f"Title: {title}\n\n"
                f"URL Source: {source_url}\n\n"
                f"Markdown Content:\n{content}"
            )

            return {
                "success": True,
                "strategy": self.name,
                "content": wrapped,
                "metadata": {"title": title, "source_url": source_url},
            }
        except Exception as e:
            return {"success": False, "error": f"Chrome CLI 错误: {e}"}
        finally:
            self._close_session_tabs(page_id)

    def _close_session_tabs(self, page_id: str = "") -> None:
        import time
        try:
            pids = [page_id] if page_id else []
            tabs = chrome_cli.send_command("tabs", op="list", session=self.session)
            for tab in tabs.get("data", []):
                pid = tab.get("page", "")
                if pid and pid not in pids:
                    pids.append(pid)
            for pid in pids:
                try:
                    chrome_cli.send_command("exec", code='location.href="about:blank"', page=pid, session=self.session)
                    time.sleep(0.3)
                    chrome_cli.send_command("exec", code="window.close()", page=pid, session=self.session)
                except Exception:
                    pass
            time.sleep(0.3)
            tabs = chrome_cli.send_command("tabs", op="list", session=self.session)
            for tab in tabs.get("data", []):
                try:
                    chrome_cli.send_command("tabs", op="close", page=tab.get("page", ""), session=self.session)
                except Exception:
                    pass
        except Exception:
            pass

    def _extract_wechat(self, page_id: str) -> dict | None:
        import time
        time.sleep(1)
        self._scroll_page(page_id)
        time.sleep(2)

        js = r"""(() => {
    const title = (document.querySelector('#activity-name') || {}).innerText?.trim() || '';
    const author = (document.querySelector('#js_name') || {}).innerText?.trim() || '';
    const pubTime = (document.querySelector('#publish_time') || {}).innerText?.trim() || '';
    const container = document.querySelector('#js_content');
    if (!container) return JSON.stringify({title, author, pubTime, url: location.href, items: []});

    const items = [];
    const processNode = (node) => {
        if (node.nodeType === 3) {
            const t = node.textContent.trim();
            if (t) items.push({t: 'text', v: t});
            return;
        }
        if (node.nodeType !== 1) return;
        const tag = node.tagName;
        if (tag === 'STYLE' || tag === 'SCRIPT') return;
        if (tag === 'IMG') {
            const src = node.getAttribute('data-src') || node.getAttribute('src') || '';
            if (src && !src.includes('wx_fed/we-emoji')) items.push({t: 'img', v: src});
            return;
        }
        if (tag === 'A') {
            const href = node.getAttribute('href') || '';
            const text = node.innerText?.trim() || '';
            if (href && text) { items.push({t: 'link', v: text, h: href}); return; }
        }
        for (const child of node.childNodes) processNode(child);
        if (/^(P|DIV|SECTION|H[1-6]|BR|LI|BLOCKQUOTE|PRE|FIGURE)$/.test(tag)) {
            items.push({t: 'br'});
        }
    };
    processNode(container);
    return JSON.stringify({title, author, pubTime, url: location.href, items});
})()"""

        try:
            result = chrome_cli.send_command("exec", code=js, page=page_id, session=self.session)
            data = result.get("data", "")
            if isinstance(data, str):
                data = json.loads(data)
            if not isinstance(data, dict):
                return None
        except Exception:
            return None

        items = data.get("items", [])
        if not items:
            return None

        parts = []
        title = data.get("title", "")
        author = data.get("author", "")
        pub_time = data.get("pubTime", "")

        if title:
            parts.append(f"# {title}\n")
        if author:
            parts.append(f"**作者**: {author}")
        if pub_time:
            parts.append(f"**发布时间**: {pub_time}")
        if parts:
            parts.append("\n---\n")

        for item in items:
            kind = item.get("t")
            if kind == "text":
                parts.append(item.get("v", ""))
            elif kind == "img":
                parts.append(f"\n![Image]({item.get('v', '')})\n")
            elif kind == "link":
                parts.append(f"[{item.get('v', '')}]({item.get('h', '')})")
            elif kind == "br":
                if parts and parts[-1] != "\n":
                    parts.append("\n")

        import re
        content = "\n".join(parts)
        content = re.sub(r'\n{3,}', '\n\n', content).strip()

        return {"title": title, "url": data.get("url", ""), "content": content}

    def _scroll_page(self, page_id: str) -> None:
        scroll_js = """(() => {
    const h = document.body.scrollHeight;
    const step = Math.max(800, Math.floor(h / 20));
    let y = 0;
    while (y < h) { y += step; window.scrollTo(0, y); }
    window.scrollTo(0, 0);
    return 'done';
})()"""
        try:
            chrome_cli.send_command("exec", code=scroll_js, page=page_id, session=self.session)
        except Exception:
            pass

    def _extract(self, page_id: str, selector: str | None) -> dict | None:
        if selector:
            js_selector = json.dumps(selector)
        else:
            js_selector = "null"

        js = f"""(() => {{
    const sel = {js_selector};
    const root = sel ? (document.querySelector(sel) || document.body) : document.body;
    const title = document.querySelector('h1')?.innerText?.trim()
        || document.title || '';
    const url = window.location.href;
    const content = root.innerText?.trim() || '';
    return JSON.stringify({{title, url, content}});
}})()"""

        try:
            result = chrome_cli.send_command("exec", code=js, page=page_id, session=self.session)
            data = result.get("data", "")
            if isinstance(data, str):
                return json.loads(data)
            return data if isinstance(data, dict) else None
        except Exception:
            if selector:
                return None
            raise
