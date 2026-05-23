"""
Markdown output formatting.
"""

import re


def format_result(result: dict, url: str, quiet: bool = False) -> str:
    """Format a read result (success or failure) as Markdown."""
    if not result.get('success'):
        if quiet:
            errors = '; '.join(result.get('errors', ['unknown error']))
            return f"[ERROR] {errors}"
        return _format_failure(result, url)
    if quiet:
        return result.get('content', '').strip()
    return _format_success(result, url)


def format_saved_result(result: dict, url: str) -> str:
    """Format a successful result for long-term LLM-friendly archiving."""
    if not result.get('success'):
        return _format_failure(result, url)

    metadata = result.get('metadata', {})
    content_type = metadata.get('content_type')
    content = result.get('content', '').strip()

    if content_type == 'social_post':
        return _format_saved_social_post(content)
    if content_type == 'forum_thread':
        return _format_saved_forum_thread(content)
    return content


def _format_success(result: dict, url: str) -> str:
    platform = result.get('platform', {})
    content = result.get('content', '')

    lines = [
        f"**来源**: {platform.get('name', '未知')}",
        f"**读取策略**: {result.get('strategy', '未知')}",
        f"**原文链接**: {url}",
        "\n---\n",
        content,
    ]
    return "\n".join(lines)


def _format_saved_social_post(content: str) -> str:
    title = _extract_title(content)
    author = _extract_labeled_value(content, '作者')
    published = _extract_labeled_value(content, '发布时间')
    images = _extract_section(content, '图片', ('正文',))
    body = _extract_section(content, '正文')

    parts = [f'# {title}']
    metadata_lines = []
    if author:
        metadata_lines.append(f'- Author: {author}')
    if published:
        metadata_lines.append(f'- Published: {published}')
    if metadata_lines:
        parts.extend(['', '## Metadata'])
        parts.extend(metadata_lines)
    if images:
        parts.extend(['', '## Images', '', images.strip()])
    if body:
        parts.extend(['', '## Content', '', body.strip()])
    return '\n'.join(parts).strip()


def _format_saved_forum_thread(content: str) -> str:
    title = _extract_title(content)
    original_poster = _extract_labeled_value(content, '楼主') or _extract_labeled_value(content, '作者')
    context = _extract_labeled_value(content, '信息')
    thread = _extract_section(content, '主楼', ('回复',)) or _extract_section(content, '帖子内容', ('回复',))
    replies_block = _extract_section(content, '回复')
    replies = _parse_numbered_replies(replies_block)

    parts = [f'# {title}']
    metadata_lines = []
    if original_poster:
        metadata_lines.append(f'- Original Poster: {original_poster}')
    if context:
        metadata_lines.append(f'- Context: {context}')
    if metadata_lines:
        parts.extend(['', '## Metadata'])
        parts.extend(metadata_lines)
    if thread:
        parts.extend(['', '## Thread', '', thread.strip()])
    if replies:
        parts.extend(['', '## Replies'])
        for index, reply in enumerate(replies, 1):
            parts.extend([
                '',
                f'### Reply {index} | {reply["header"]}',
                '',
                _normalize_reply_body(reply['body']),
            ])
    return '\n'.join(parts).strip()


def _format_failure(result: dict, url: str) -> str:
    lines = [
        "# 读取失败\n",
        f"**URL**: {url}",
        f"**平台**: {result.get('platform', {}).get('name', '未知')}",
        "\n**尝试的策略及错误**:",
    ]
    for err in result.get('errors', []):
        lines.append(f"- {err}")
    lines.extend([
        "\n**建议**:",
        "1. 如果是微信公众号，请运行 `python -m scripts.wechat_auth setup` 设置登录态",
        "2. 设置 FIRECRAWL_API_KEY 环境变量以使用 Firecrawl",
        "3. 或手动复制文章内容",
    ])
    return "\n".join(lines)


def _extract_title(content: str) -> str:
    match = re.search(r'(?m)^#\s+(.+)$', content)
    return match.group(1).strip() if match else 'untitled'


def _extract_labeled_value(content: str, label: str) -> str:
    match = re.search(rf'(?m)^\*\*{re.escape(label)}\*\*:\s*(.+)$', content)
    return match.group(1).strip() if match else ''


def _extract_section(content: str, heading: str, next_headings: tuple[str, ...] = ()) -> str:
    escaped_heading = re.escape(heading)
    if next_headings:
        next_pattern = '|'.join(re.escape(item) for item in next_headings)
        pattern = rf'(?ms)^##\s+{escaped_heading}\s*\n+(.*?)(?=^##\s+(?:{next_pattern})\s*$|\Z)'
    else:
        pattern = rf'(?ms)^##\s+{escaped_heading}\s*\n+(.*)$'
    match = re.search(pattern, content)
    return match.group(1).strip() if match else ''


def _parse_numbered_replies(replies_block: str) -> list[dict[str, str]]:
    if not replies_block.strip():
        return []
    pattern = re.compile(r'(?ms)^(?P<index>\d+)\.\s+(?P<header>.+?)\n(?P<body>.*?)(?=^\d+\.\s+|\Z)')
    replies: list[dict[str, str]] = []
    for match in pattern.finditer(replies_block.strip()):
        replies.append({
            'header': match.group('header').strip(),
            'body': match.group('body').strip(),
        })
    return replies


def _normalize_reply_body(body: str) -> str:
    lines = [line.rstrip() for line in body.splitlines()]
    cleaned: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if cleaned and cleaned[-1] != '':
                cleaned.append('')
            continue
        stripped = re.sub(r'@([^\s@#\[]+?)#(\d+)', r'@\1 (#\2)', stripped)
        stripped = re.sub(r'@([^\s@]+)\s+\[#(\d+)\]', r'@\1 (#\2)', stripped)
        mentions = re.findall(r'@(.+?)\s+\(#(\d+)\)(?=\s*@|$)', stripped)
        if mentions and ''.join(f'@{name} (#{floor})' for name, floor in mentions) == stripped.replace('  ', ' '):
            stripped = 'Mentioned floors: ' + ', '.join(f'@{name} (#{floor})' for name, floor in mentions)
        cleaned.append(stripped)
    text = '\n'.join(cleaned)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
