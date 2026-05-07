"""
Content utilities: title extraction, image extraction, filename sanitization.
Pure utility module with no internal imports.
"""

import re
from urllib.parse import urlparse

_CLEANUP_RULES = {
    'generic': {
        'window_start_markers': (),
        'tail_markers': (
            '相关阅读',
            '相关推荐',
            '推荐阅读',
            '猜你喜欢',
            '热门评论',
            '全部评论',
            '发表评论',
            'Leave a Reply',
            'Leave a Comment',
            '相关文章',
            'Related Posts',
            '评论 取消',
            '您的电子邮箱',
            '必填项已用',
        ),
        'drop_exact': {
            '首页', '登录', '注册', '下载APP', '下载 App', '打开APP', '打开 App',
            '分享', '收藏', '举报', '反馈',
        },
        'drop_prefixes': (
            '上一篇', '下一篇', '相关阅读', '相关推荐', '推荐阅读', '热门推荐',
            '猜你喜欢', '更多推荐',
        ),
        'drop_contains': (
            'ICP备',
            '版权所有',
            '隐私政策',
            '网站地图',
            '联系我们',
            '免责声明',
            'Proudly powered by WordPress',
            'Built with WordPress',
        ),
        'drop_regexes': (
            r'^[\s\W_]+$',
            r'^\d+\s*$',
            r'^\d+\s*/\s*\d+\s*$',
        ),
    },
    'article_feed': {
        'window_start_markers': (),
        'tail_markers': (
            '相关推荐',
            '相关阅读',
            '推荐阅读',
            '更多精彩内容',
            '全部评论',
            '评论区',
            '热门评论',
        ),
        'drop_exact': {
            '写评论', '暂无评论', '打开APP阅读全文', '打开 App 阅读全文',
        },
        'drop_prefixes': (
            '关注作者',
            '进入专栏',
            '展开全文',
        ),
        'drop_contains': (
            '登录后参与评论',
            '下载知乎客户端',
            '打开今日头条',
        ),
        'drop_regexes': (
            r'^\d+\s*(赞|评论|收藏|转发)$',
            r'^[\s\W_]+$',
            r'^\d+\s*$',
        ),
    },
    'wechat_article': {
        'window_start_markers': (),
        'tail_markers': (
            '继续滑动看下一个',
            '阅读原文',
            '写留言',
            '留言',
            '推荐阅读',
            '微信扫一扫关注该公众号',
            '预览时标签不可点',
            '喜欢此内容的人还喜欢',
        ),
        'drop_exact': {
            '微信扫一扫关注该公众号',
            '点击阅读原文',
            '阅读原文',
        },
        'drop_prefixes': (
            '点击上方',
            '长按识别',
            '继续滑动看下一个',
        ),
        'drop_contains': (
            '喜欢此内容的人还喜欢',
            '预览时标签不可点',
        ),
        'drop_regexes': (
            r'^[\s\W_]+$',
            r'^\d+\s*$',
        ),
    },
    'social_note': {
        'window_start_markers': (),
        'tail_markers': (
            '全部评论',
            '评论区',
            '相关推荐',
            '大家都在搜',
            '热门推荐',
            '猜你喜欢',
        ),
        'drop_exact': {
            '小红书', '微博正文', '赞', '评论', '转发', '收藏', '分享',
            '打开小红书', '打开微博', '下载小红书 App',
        },
        'drop_prefixes': (
            '打开小红书',
            '打开微博',
            '下载小红书',
            '查看全部评论',
            '查看更多评论',
        ),
        'drop_contains': (
            '作者赞过',
            '发布于',
            '编辑于',
            '来自微博',
            '来自 iPhone',
            '来自 Android',
        ),
        'drop_regexes': (
            r'^\d+\s*(赞|评论|收藏|转发)$',
            r'^\d+(\.\d+)?[万wW]?$',
            r'^[\s\W_]+$',
        ),
    },
    'short_video': {
        'window_start_markers': (),
        'tail_markers': (
            '相关推荐',
            '猜你喜欢',
            '热门评论',
            '全部评论',
        ),
        'drop_exact': {
            '弹幕', '点赞', '投币', '收藏', '转发', '评论',
        },
        'drop_prefixes': (
            '打开抖音',
            '打开哔哩哔哩',
            '下载抖音',
            '下载哔哩哔哩',
        ),
        'drop_contains': (
            '上滑查看更多',
            '打开APP观看',
        ),
        'drop_regexes': (
            r'^\d+\s*(赞|评论|收藏|投币|转发)$',
            r'^\d+(\.\d+)?[万wW]?$',
            r'^[\s\W_]+$',
        ),
    },
    'meowvps': {
        'tail_min_offset': 10,
        'window_start_markers': (),
        'tail_markers': (
            '发表评论',
            'Leave a Reply',
            '相关文章',
            'Related Posts',
            '上一篇',
            '下一篇',
            '评论 取消',
            '您的电子邮箱',
            '必填项已用',
            '猜你喜欢',
            '商家目录',
            '最新优惠',
            '标签云',
        ),
        'drop_exact': {
            '首页', '商家', '优惠', '工具', '博客', '关于',
            'Home', 'Vendors', 'Deals', 'Tools', 'Blog', 'About',
            '搜索', '搜索:', 'Search', '登录', '注册',
            '复制链接', '分享到微信', '分享到QQ', '分享到微博',
            '目录', 'Table of Contents',
        },
        'drop_prefixes': (
            '商家目录',
            '最新优惠',
            '标签云',
            '热门标签',
            '最近文章',
            '搜索:',
            '© ',
            'Copyright',
            '筛选',
            '排序',
            '所有商家',
            '所有地区',
        ),
        'drop_contains': (
            'meowvps.com',
            '版权所有',
            'ICP备',
            '粤ICP',
            '京ICP',
            '输入关键词',
            '开始搜索',
        ),
        'drop_regexes': (
            r'^[\s\W_]+$',
            r'^\d+\s*$',
            r'^第\s*\d+\s*页',
            r'^\d+\s*/\s*\d+\s*$',
        ),
    },
    'forum_thread': {
        'window_start_markers': (),
        'tail_markers': (
            '快速回复',
            '发表回复',
            '返回列表',
            '您需要登录后才可以回帖',
            '本版积分规则',
        ),
        'drop_exact': {
            '返回列表', '发新帖', '回复', '使用道具', '举报',
            '高级模式', 'B Color Image Link Quote Code Smilies',
        },
        'drop_prefixes': (
            'Powered by Discuz',
            'GMT+',
            '快速回复',
            '返回顶部',
        ),
        'drop_contains': (
            'Powered by Discuz',
            '积分规则',
            'Archiver',
            '手机版',
            '小黑屋',
        ),
        'drop_regexes': (
            r'^[\s\W_]+$',
            r'^\d+\s*$',
            r'^\d+#',
        ),
    },
    'ecommerce': {
        'start_match': 'exact',
        'start_marker_priority': True,
        'tail_match': 'startswith',
        'tail_min_offset': 20,
        'window_start_markers': (
            '商品详情',
            '规格参数',
            '参数信息',
            '商品参数',
        ),
        'tail_markers': (
            '售后保障',
            '京东承诺',
            '权利声明',
            '购物指南',
            '关于我们',
            '看了又看',
            '配送方式',
            '支付方式',
        ),
        'drop_exact': {
            '首页', '购物车', '我的', '客服', '反馈', '收起', '展开全部',
            '加入购物车', '立即购买', '进店逛逛', '联系客服', '领券', '收藏',
        },
        'drop_prefixes': (
            '京东首页',
            '中国大陆版',
            '店铺关注',
            '累计评价',
            '配送方式',
            '支付方式',
            '售后服务',
            '购物指南',
        ),
        'drop_contains': (
            '品类齐全，轻松购物',
            '多仓直发，极速配送',
            '正品行货，精致服务',
            '天天低价，畅选无忧',
            '京公网安备',
            'ICP备',
            'Copyright',
            '友情链接',
            '营业执照',
            '增值电信业务经营许可证',
            '售后服务电话',
        ),
        'drop_regexes': (
            r'^￥\s*\d',
            r'^[\s\W_]+$',
        ),
    },
}


def sanitize_filename(name: str, max_length: int = 50) -> str:
    """Remove illegal characters and truncate."""
    name = re.sub(r'[<>:"/\\|?*\n\r\t]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    if len(name) > max_length:
        name = name[:max_length]
    return name or "untitled"


def extract_title(content: str) -> str:
    """Extract a title from Markdown content."""
    # Markdown h1
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        if title and not title.startswith('来源') and not title.startswith('**') and len(title) > 2:
            return title

    # **标题**: format
    match = re.search(r'\*\*标题\*\*[：:]\s*(.+)', content)
    if match:
        return match.group(1).strip()

    # First meaningful line
    for line in content.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('**') or line.startswith('---') or line.startswith('#'):
            continue
        if 5 < len(line) < 100:
            return line[:50]

    return "untitled"


def extract_images(content: str) -> list[str]:
    """Extract all image URLs from Markdown/HTML content, deduplicated."""
    md_images = re.findall(r'!\[.*?\]\((https?://[^\s\)]+)\)', content)
    direct_images = re.findall(
        r'(https?://[^\s\)]+\.(?:jpg|jpeg|png|gif|webp|bmp)[^\s\)]*)',
        content, re.IGNORECASE,
    )
    xhs_images = re.findall(r'(https?://sns-webpic[^\s\)]+)', content)
    feishu_images = re.findall(
        r'(https?://[^\s\)]*feishu[^\s\)]+\.(?:jpg|jpeg|png|gif|webp)[^\s\)]*)',
        content, re.IGNORECASE,
    )
    qq_images = re.findall(
        r'(https?://docimg[^\s\)]+\.(?:jpg|jpeg|png|gif|webp)[^\s\)]*)',
        content, re.IGNORECASE,
    )
    return list(dict.fromkeys(md_images + direct_images + xhs_images + feishu_images + qq_images))


def detect_verification_page(text: str) -> bool:
    """
    Detect whether text is a verification/captcha page.
    Uses compound phrase check in first 500 chars to avoid false positives.
    """
    snippet = text[:500]
    return '环境异常' in snippet and '完成验证' in snippet


def postprocess_content(content: str, url: str, platform: dict) -> dict:
    """Normalize strategy output and apply forum-specific extraction rules."""
    metadata = _extract_jina_metadata(content)
    markdown = metadata.get('markdown', content).strip()

    if _is_zhihu_question_page(platform, url):
        return _extract_zhihu_question_answers(markdown, metadata)

    if _is_forum_platform(platform, url):
        return _extract_forum_thread(markdown, platform, url, metadata)

    if _is_x_platform(platform, url):
        return _extract_x_post(markdown, metadata)

    cleaned, cleanup_stats = _apply_platform_cleanup(markdown, platform)
    picked_title = _pick_title(cleaned, metadata)

    merged_metadata = {
        **metadata,
        **cleanup_stats,
    }
    if picked_title and picked_title != 'untitled':
        merged_metadata['title'] = picked_title

    return {
        'success': True,
        'content': cleaned,
        'metadata': merged_metadata,
    }


def extract_forum_replies_page(content: str, url: str, platform: dict) -> list[dict[str, str]]:
    """Extract replies from forum pagination pages without rebuilding the main post."""
    metadata = _extract_jina_metadata(content)
    markdown = metadata.get('markdown', content).strip()
    lowered = markdown.lower()
    if any(
        token in lowered for token in (
            'just a moment',
            'enable javascript and cookies to continue',
            '# sign in',
            'discussion not found',
        )
    ):
        return []

    if platform.get('id') not in {'lowendtalk', 'lowendspirit'}:
        return []

    if markdown.lstrip().startswith('## Comments'):
        comments_block = markdown.split('## Comments', 1)[1]
        return _extract_vanilla_replies(comments_block)

    if '\n## Comments' in markdown:
        comments_block = markdown.split('\n## Comments', 1)[1]
        return _extract_vanilla_replies(comments_block)

    return []


def _is_forum_platform(platform: dict, url: str) -> bool:
    forum_ids = {'nodeseek', 'lowendtalk', 'lowendspirit', 'hostloc', 'linuxdo', 'v2ex'}
    if platform.get('id') in forum_ids:
        return True

    path = urlparse(url).path.lower()
    return '/discussion/' in path or '/post-' in path


def _is_x_platform(platform: dict, url: str) -> bool:
    if platform.get('id') == 'x':
        return True

    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    return any(token in domain for token in ('x.com', 'twitter.com')) and '/status/' in parsed.path.lower()


def _is_zhihu_question_page(platform: dict, url: str) -> bool:
    if platform.get('id') != 'zhihu':
        return False
    return '/question/' in urlparse(url).path.lower()


def _extract_jina_metadata(content: str) -> dict:
    metadata: dict[str, str] = {}

    title_match = re.search(r'^Title:\s*(.+)$', content, re.MULTILINE)
    if title_match:
        metadata['jina_title'] = title_match.group(1).strip()

    source_match = re.search(r'^URL Source:\s*(.+)$', content, re.MULTILINE)
    if source_match:
        metadata['source_url'] = source_match.group(1).strip()

    published_match = re.search(r'^Published Time:\s*(.+)$', content, re.MULTILINE)
    if published_match:
        metadata['published_time'] = published_match.group(1).strip()

    if 'Markdown Content:' in content:
        metadata['markdown'] = content.split('Markdown Content:', 1)[1].strip()
    else:
        metadata['markdown'] = content.strip()

    return metadata


def _apply_platform_cleanup(markdown: str, platform: dict) -> tuple[str, dict]:
    profile = platform.get('cleanup_profile', 'generic')
    rules = _CLEANUP_RULES.get(profile) or _CLEANUP_RULES['generic']

    source_lines = markdown.splitlines()
    if not source_lines:
        return markdown.strip(), {
            'cleanup_profile': profile,
            'cleanup_chars_before': len(markdown),
            'cleanup_chars_after': len(markdown.strip()),
            'cleanup_ratio': 1.0,
        }

    scoped_lines = _slice_lines_by_markers(
        source_lines,
        rules.get('window_start_markers', ()),
        rules.get('tail_markers', ()),
        start_match=rules.get('start_match', 'contains'),
        start_marker_priority=rules.get('start_marker_priority', False),
        tail_match=rules.get('tail_match', 'contains'),
        tail_min_offset=rules.get('tail_min_offset', 0),
    )

    cleaned_lines: list[str] = []
    for raw_line in scoped_lines:
        line = raw_line.strip()
        if not line:
            if cleaned_lines and cleaned_lines[-1] != '':
                cleaned_lines.append('')
            continue

        normalized_image = _normalize_link_wrapped_image(line)
        normalized_line = normalized_image or _collapse_spaces(line)
        if _is_platform_noise_line(normalized_line, rules):
            continue

        if cleaned_lines and normalized_line == cleaned_lines[-1]:
            continue

        if len(normalized_line) <= 2 and not re.search(r'[\u4e00-\u9fffA-Za-z0-9]', normalized_line):
            continue

        cleaned_lines.append(normalized_line)

    cleaned = _join_paragraphs(cleaned_lines)
    if not cleaned:
        cleaned = markdown.strip()
    elif len(cleaned) < 80 and len(markdown.strip()) > 500:
        # Avoid over-pruning on noisy pages where markers match too early.
        cleaned = _fallback_dedupe(markdown)

    before = len(markdown.strip())
    after = len(cleaned.strip())
    ratio = round(after / before, 4) if before else 1.0
    return cleaned, {
        'cleanup_profile': profile,
        'cleanup_chars_before': before,
        'cleanup_chars_after': after,
        'cleanup_ratio': ratio,
    }


def _slice_lines_by_markers(
    lines: list[str],
    start_markers: tuple[str, ...],
    tail_markers: tuple[str, ...],
    start_match: str = 'contains',
    start_marker_priority: bool = False,
    tail_match: str = 'contains',
    tail_min_offset: int = 0,
) -> list[str]:
    scoped = lines
    start_idx = _find_marker_line(
        lines,
        start_markers,
        match_mode=start_match,
        marker_priority=start_marker_priority,
    )
    if start_idx != -1:
        scoped = lines[start_idx:]

    tail_idx = _find_marker_line(
        scoped,
        tail_markers,
        match_mode=tail_match,
        marker_priority=False,
        min_index=max(0, tail_min_offset),
    )
    if tail_idx != -1:
        scoped = scoped[:tail_idx]
    return scoped


def _find_marker_line(
    lines: list[str],
    markers: tuple[str, ...],
    match_mode: str = 'contains',
    marker_priority: bool = False,
    min_index: int = 0,
) -> int:
    if not markers:
        return -1

    lowered_markers = [marker.lower() for marker in markers if marker]
    if not lowered_markers:
        return -1

    if marker_priority:
        for marker in lowered_markers:
            for idx, raw_line in enumerate(lines):
                if idx < min_index:
                    continue
                if _line_matches_marker(raw_line.strip().lower(), marker, match_mode):
                    return idx
        return -1

    for idx, raw_line in enumerate(lines):
        if idx < min_index:
            continue
        lowered_line = raw_line.strip().lower()
        for marker in lowered_markers:
            if _line_matches_marker(lowered_line, marker, match_mode):
                return idx
    return -1


def _line_matches_marker(line: str, marker: str, match_mode: str) -> bool:
    if match_mode == 'exact':
        return line == marker
    if match_mode == 'startswith':
        return line.startswith(marker)
    return marker in line


def _is_platform_noise_line(line: str, rules: dict) -> bool:
    lowered = line.lower()

    if line in rules.get('drop_exact', set()):
        return True

    for prefix in rules.get('drop_prefixes', ()):
        if prefix and lowered.startswith(prefix.lower()):
            return True

    for token in rules.get('drop_contains', ()):
        if token and token.lower() in lowered:
            return True

    for pattern in rules.get('drop_regexes', ()):
        if re.search(pattern, line):
            return True

    return False


def _collapse_spaces(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def _fallback_dedupe(markdown: str) -> str:
    lines: list[str] = []
    for raw_line in markdown.splitlines():
        line = _collapse_spaces(raw_line)
        if not line:
            if lines and lines[-1] != '':
                lines.append('')
            continue
        if lines and lines[-1] == line:
            continue
        lines.append(line)
    return _join_paragraphs(lines)


def _extract_forum_thread(markdown: str, platform: dict, url: str, metadata: dict) -> dict:
    lowered = markdown.lower()
    if any(
        token in lowered for token in (
            'just a moment',
            'enable javascript and cookies to continue',
            '# sign in',
            'discussion not found',
        )
    ):
        return {'success': False, 'error': '未获取到公开帖子正文'}

    if platform.get('id') == 'nodeseek':
        cleaned = _extract_nodeseek_thread(markdown, metadata)
    elif platform.get('id') == 'hostloc':
        cleaned = _extract_hostloc_thread(markdown, metadata)
    elif platform.get('id') == 'linuxdo':
        cleaned = _extract_linuxdo_thread(markdown, metadata)
    elif platform.get('id') == 'v2ex':
        cleaned = _extract_v2ex_thread(markdown, metadata)
    else:
        cleaned = _extract_vanilla_forum_thread(markdown, metadata)

    if len(cleaned.strip()) < 80:
        return {'success': False, 'error': '帖子正文提取失败'}

    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': extract_title(cleaned),
            'content_type': 'forum_thread',
        },
    }


def _extract_nodeseek_thread(markdown: str, metadata: dict) -> str:
    title = _clean_inline_markdown(_pick_title(markdown, metadata))
    body = markdown

    detailed_heading = f'# [{title}]('
    if detailed_heading in body:
        body = body.split(detailed_heading, 1)[1]
        close_idx = body.find(')')
        if close_idx != -1:
            body = body[close_idx + 1:].strip()
    else:
        first_heading = f'# {title}'
        if first_heading in body:
            body = body.split(first_heading, 1)[1].strip()

    author = ''
    author_match = re.search(r'\[([^\]]+)\]\([^)]+\)楼主', body)
    if author_match:
        author = author_match.group(1).strip()

    meta_line = ''
    meta_match = re.search(r'\n([^\n]*?\bin\b\s+\[[^\]]+\]\([^)]+\))', body)
    if meta_match:
        meta_line = _clean_inline_markdown(meta_match.group(1))

    replies: list[dict[str, str]] = []
    thread_body = body
    main_marker = re.search(r'\[#0\]\([^)]+\)\s*', body)
    if main_marker:
        thread_body = body[main_marker.end():]
    thread_body = _truncate_nodeseek_tail(thread_body)
    reply_header_pattern = re.compile(
        r'^\*\s+\[!\[Image.*?\]\([^)]+\)\]\([^)]+\)\s+\[(?P<user>[^\]]+)\]\([^)]+\)'
        r'(?:楼主)?\s+(?P<time>.+?)\s+\[#(?P<floor>\d+)\]\([^)]+\)\s*$'
    )

    main_lines: list[str] = []
    current_reply: dict[str, str] | None = None
    current_reply_lines: list[str] = []

    for raw_line in thread_body.splitlines():
        line = raw_line.strip()
        match = reply_header_pattern.match(line)
        if match:
            if current_reply is not None:
                reply_body = _clean_nodeseek_body('\n'.join(current_reply_lines))
                if _should_keep_reply(reply_body):
                    replies.append({
                        'header': current_reply['header'],
                        'body': reply_body or '(无正文)',
                    })

            current_reply = {
                'header': (
                    f'{match.group("user").strip()} | '
                    f'{match.group("time").strip()} | '
                    f'#{match.group("floor")}'
                ),
            }
            current_reply_lines = []
            continue

        if current_reply is None:
            main_lines.append(raw_line)
        else:
            current_reply_lines.append(raw_line)

    if current_reply is not None:
        reply_body = _clean_nodeseek_body('\n'.join(current_reply_lines))
        if _should_keep_reply(reply_body):
            replies.append({
                'header': current_reply['header'],
                'body': reply_body or '(无正文)',
            })

    main_post = _clean_nodeseek_body('\n'.join(main_lines))

    parts = [f'# {title}']
    if author:
        parts.append(f'**楼主**: {author}')
    if meta_line:
        parts.append(f'**信息**: {meta_line}')

    parts.append('\n## 主楼\n')
    parts.append(main_post or '未提取到主楼正文')

    if replies:
        parts.append('\n## 回复\n')
        for idx, reply in enumerate(replies, 1):
            parts.append(f'{idx}. {reply["header"]}')
            parts.append(reply['body'] or '(无正文)')

    return '\n'.join(parts).strip()


def _extract_vanilla_forum_thread(markdown: str, metadata: dict) -> str:
    title = _clean_inline_markdown(_pick_title(markdown, metadata))
    body = markdown

    marker = f'# {title}'
    if body.count(marker) >= 2:
        body = body.rsplit(marker, 1)[1]
    elif marker in body:
        body = body.split(marker, 1)[1]

    comments_block = ''
    if '\n## Comments' in body:
        body, comments_block = body.split('\n## Comments', 1)

    body = re.split(r'\n(?:\[Sign In\].*?to comment\.|#### Howdy, Stranger!|#### Categories|#### In this Discussion|© LowEndSpirit|Back to Top)', body, 1, re.S)[0]

    raw_lines = [line.rstrip() for line in body.splitlines()]
    kept_lines: list[str] = []
    author = ''
    meta_line = ''

    for raw_line in raw_lines:
        line = raw_line.strip()
        if not line:
            if kept_lines and kept_lines[-1] != '':
                kept_lines.append('')
            continue

        if _is_vanilla_forum_noise(line):
            continue

        cleaned = _clean_inline_markdown(line)
        if not cleaned:
            continue

        if not author and not meta_line and not kept_lines and ('/profile/' in raw_line or re.search(r'(Moderator|Member|Vendor|OG|Retired|Administrator)', cleaned)):
            author = cleaned
            continue

        if not meta_line and (' in ' in cleaned or 'edited ' in cleaned or re.search(r'\b\d{4}\b', cleaned)):
            meta_line = cleaned
            continue

        kept_lines.append(cleaned)

    while kept_lines and kept_lines[-1] == '':
        kept_lines.pop()

    parts = [f'# {title}']
    if author:
        parts.append(f'**作者**: {author}')
    if meta_line:
        parts.append(f'**信息**: {meta_line}')

    parts.append('\n## 帖子内容\n')
    parts.append(_join_paragraphs(kept_lines) or '未提取到帖子正文')

    replies = _extract_vanilla_replies(comments_block)
    if replies:
        parts.append('\n## 回复\n')
        for idx, reply in enumerate(replies, 1):
            parts.append(f'{idx}. {reply["header"]}')
            parts.append(reply['body'])
    return '\n'.join(parts).strip()


def _extract_hostloc_thread(markdown: str, metadata: dict) -> str:
    title = _clean_inline_markdown(_pick_title(markdown, metadata))
    body = markdown

    marker = f'# {title}'
    if marker in body:
        body = body.split(marker, 1)[1]

    body = _truncate_hostloc_tail(body)

    raw_lines = body.splitlines()
    kept_lines: list[str] = []
    author = ''
    replies: list[dict[str, str]] = []
    current_reply: dict[str, str] | None = None
    current_reply_lines: list[str] = []

    reply_pattern = re.compile(
        r'^\*?\s*(?:\[?!\[.*?\]\([^)]+\)\]?\([^)]+\))?\s*\[?([^\]]+)\]?\(?[^)]*\)?\s*'
        r'.*?发表于\s*(.+?)$'
    )
    floor_pattern = re.compile(r'^\d+#\s*$')

    for raw_line in raw_lines:
        line = raw_line.strip()

        if not line or _is_hostloc_noise(line):
            if current_reply is not None:
                if current_reply_lines and current_reply_lines[-1] != '':
                    current_reply_lines.append('')
            elif kept_lines and kept_lines[-1] != '':
                kept_lines.append('')
            continue

        if floor_pattern.match(line):
            continue

        reply_match = reply_pattern.match(line)
        if reply_match and (kept_lines or current_reply is not None):
            if current_reply is not None:
                reply_body = _clean_inline_markdown('\n'.join(current_reply_lines))
                if _should_keep_reply(reply_body):
                    replies.append({'header': current_reply['header'], 'body': reply_body or '(无正文)'})
            current_reply = {
                'header': f'{reply_match.group(1).strip()} | {reply_match.group(2).strip()}'
            }
            current_reply_lines = []
            continue

        cleaned = _clean_inline_markdown(line)
        if not cleaned:
            continue

        if not author and not kept_lines and ('楼主' in line or '发表于' in line):
            author_match = re.search(r'(?<!!)\[([^\]!][^\]]*)\]\([^)]+\)', line)
            if author_match:
                author = author_match.group(1).strip()
            continue

        if current_reply is not None:
            current_reply_lines.append(cleaned)
        else:
            kept_lines.append(cleaned)

    if current_reply is not None:
        reply_body = _clean_inline_markdown('\n'.join(current_reply_lines))
        if _should_keep_reply(reply_body):
            replies.append({'header': current_reply['header'], 'body': reply_body or '(无正文)'})

    parts = [f'# {title}']
    if author:
        parts.append(f'**楼主**: {author}')
    parts.append('\n## 帖子内容\n')
    parts.append(_join_paragraphs(kept_lines) or '未提取到帖子正文')

    if replies:
        parts.append('\n## 回复\n')
        for idx, reply in enumerate(replies, 1):
            parts.append(f'{idx}. {reply["header"]}')
            parts.append(reply['body'])

    return '\n'.join(parts).strip()


def _extract_linuxdo_thread(markdown: str, metadata: dict) -> str:
    raw_title = metadata.get('jina_title') or _pick_title(markdown, metadata)
    title = _clean_inline_markdown(re.sub(r'\s+-\s+.+?\s+-\s+LINUX DO$', '', raw_title).strip())
    body = _truncate_linuxdo_tail(markdown)

    reply_header_pattern = re.compile(r'^## post by (?P<user>.+?) (?P<time>.+?)$')

    author = ''
    main_post = ''
    replies: list[dict[str, str]] = []
    current_reply: dict[str, str] | None = None
    current_reply_lines: list[str] = []
    post_index = 0

    for raw_line in body.splitlines():
        line = raw_line.strip()
        match = reply_header_pattern.match(line)
        if match:
            if current_reply is not None:
                reply_body = _clean_linuxdo_body('\n'.join(current_reply_lines))
                if post_index == 0:
                    main_post = reply_body
                elif _should_keep_reply(reply_body):
                    replies.append({
                        'header': f'{current_reply["user"]} | {current_reply["time"]}',
                        'body': reply_body or '(无正文)',
                    })
                post_index += 1

            current_reply = {
                'user': match.group('user').strip(),
                'time': match.group('time').strip(),
            }
            if not author:
                author = current_reply['user']
            current_reply_lines = []
            continue

        if current_reply is None:
            continue

        current_reply_lines.append(raw_line)

    if current_reply is not None:
        reply_body = _clean_linuxdo_body('\n'.join(current_reply_lines))
        if post_index == 0:
            main_post = reply_body
        elif _should_keep_reply(reply_body):
            replies.append({
                'header': f'{current_reply["user"]} | {current_reply["time"]}',
                'body': reply_body or '(无正文)',
            })

    parts = [f'# {title}']
    if author:
        parts.append(f'**楼主**: {author}')
    if metadata.get('published_time'):
        parts.append(f'**发布时间**: {metadata["published_time"]}')
    parts.append('\n## 主楼\n')
    parts.append(main_post or '未提取到主楼正文')

    if replies:
        parts.append('\n## 回复\n')
        for idx, reply in enumerate(replies, 1):
            parts.append(f'{idx}. {reply["header"]}')
            parts.append(reply['body'])

    return '\n'.join(parts).strip()


def _extract_v2ex_thread(markdown: str, metadata: dict) -> str:
    title = _clean_inline_markdown(_pick_v2ex_title(markdown, metadata))
    body = markdown

    linked_title_marker = f'# {title}'
    if body.count(linked_title_marker) >= 2:
        body = body.rsplit(linked_title_marker, 1)[1]
    elif linked_title_marker in body:
        body = body.split(linked_title_marker, 1)[1]

    body = _truncate_v2ex_tail(body)

    replies_marker = re.search(r'\n\d+\s+replies\s+\*\*•\*\*.*', body)
    replies_block = ''
    if replies_marker:
        replies_block = body[replies_marker.end():]
        body = body[:replies_marker.start()]

    author = ''
    meta_line = ''
    main_lines: list[str] = []
    member_link_pattern = re.compile(r'^\[([^\]]+)\]\(https://www\.v2ex\.com/member/[^)]+\)')

    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            if main_lines and main_lines[-1] != '':
                main_lines.append('')
            continue

        if line == '深入探索':
            break
        if _is_v2ex_noise(line):
            continue

        if not author:
            author_match = member_link_pattern.match(line)
            if author_match:
                author = author_match.group(1).strip()
                continue

        if not meta_line and re.search(r'\bviews\b', line):
            meta_line = _clean_inline_markdown(line)
            continue

        cleaned = line if _normalize_link_wrapped_image(line) or line.startswith('![') else _clean_inline_markdown(line)
        if cleaned:
            main_lines.append(cleaned)

    replies = _extract_v2ex_replies(replies_block)

    parts = [f'# {title}']
    if author:
        parts.append(f'**楼主**: {author}')
    if metadata.get('published_time'):
        parts.append(f'**发布时间**: {metadata["published_time"]}')
    elif meta_line:
        parts.append(f'**信息**: {meta_line}')
    parts.append('\n## 主楼\n')
    parts.append(_join_paragraphs(main_lines) or '未提取到主楼正文')

    if replies:
        parts.append('\n## 回复\n')
        for idx, reply in enumerate(replies, 1):
            parts.append(f'{idx}. {reply["header"]}')
            parts.append(reply['body'])

    return '\n'.join(parts).strip()


def _truncate_hostloc_tail(text: str) -> str:
    markers = (
        '\n快速回复',
        '\n发表回复',
        '\n返回列表',
        '\n您需要登录后才可以回帖',
        '\n本版积分规则',
        '\nPowered by Discuz',
        '\nGMT+',
        '\n发新帖',
    )
    cut_points = [text.find(marker) for marker in markers if text.find(marker) != -1]
    if cut_points:
        return text[:min(cut_points)].rstrip()
    return text


def _is_hostloc_noise(line: str) -> bool:
    lowered = line.lower()
    if 'powered by discuz' in lowered:
        return True
    if line in {'使用道具', '举报', '回复', '发新帖', '返回列表', '高级模式'}:
        return True
    if line == 'B Color Image Link Quote Code Smilies':
        return True
    if '积分' in line and '威望' in line:
        return True
    if '注册时间' in line or '最后登录' in line:
        return True
    if re.fullmatch(r'\d+#', line):
        return True
    if re.fullmatch(r'[\s\W_]+', line):
        return True
    if line.startswith('本帖最后由') and '编辑' in line:
        return True
    return False


def _pick_title(markdown: str, metadata: dict) -> str:
    title = extract_title(markdown)
    if title != 'untitled':
        return re.sub(r'\s+[—-]\s+LowEnd(?:Talk|Spirit)$', '', title).strip()

    jina_title = metadata.get('jina_title', '')
    if jina_title:
        return re.sub(r'\s+[—-]\s+LowEnd(?:Talk|Spirit)$', '', jina_title).strip()

    return 'untitled'


def _pick_v2ex_title(markdown: str, metadata: dict) -> str:
    jina_title = metadata.get('jina_title', '')
    if jina_title:
        return re.sub(r'\s*-\s*V2EX$', '', jina_title).strip()
    return _pick_title(markdown, metadata)


def _extract_x_post(markdown: str, metadata: dict) -> dict:
    title = _pick_x_title(markdown, metadata)
    author = _pick_x_author(metadata)
    images: list[str] = []
    body_lines: list[str] = []

    for raw_line in _truncate_x_tail(markdown).splitlines():
        line = raw_line.strip()
        if not line or _is_x_noise(line):
            continue

        image_line = _normalize_link_wrapped_image(line)
        if image_line:
            images.append(image_line)
            continue

        cleaned = _clean_inline_markdown(line)
        if not cleaned or cleaned == title:
            continue
        body_lines.append(cleaned)

    body = _join_paragraphs(body_lines)
    if len(body.strip()) < 20:
        return {'success': False, 'error': 'X 帖子正文提取失败'}

    parts = [f'# {title}']
    if author:
        parts.append(f'**作者**: {author}')
    if metadata.get('published_time'):
        parts.append(f'**发布时间**: {metadata["published_time"]}')
    if images:
        parts.append('\n## 图片\n')
        parts.extend(images)
    parts.append('\n## 正文\n')
    parts.append(body)

    cleaned = '\n'.join(parts).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': title,
            'content_type': 'social_post',
        },
    }


def _extract_zhihu_question_answers(markdown: str, metadata: dict) -> dict:
    title = _pick_zhihu_question_title(markdown, metadata)
    answer_start = re.search(r'(?m)^####\s+\d+\s+个回答\s*$', markdown)
    if not answer_start:
        return {'success': False, 'error': '知乎问题回答区提取失败'}

    answer_block = markdown[answer_start.end():]
    answers: list[dict[str, str]] = []
    current_author = ''
    current_lines: list[str] = []
    author_pattern = re.compile(r'^\[([^\]]+)\]\((?:https?:)?//www\.zhihu\.com/people/[^)]+\)$')
    avatar_pattern = re.compile(r'^\[!\[[^\]]*\]\([^)]+\)\]\((?:https?:)?//www\.zhihu\.com/people/[^)]+\)$')

    def flush_answer() -> None:
        nonlocal current_author, current_lines
        if not current_author:
            current_lines = []
            return
        body = _clean_zhihu_answer_body(current_lines)
        if body:
            answers.append({'author': current_author, 'body': body})
        current_author = ''
        current_lines = []

    for raw_line in answer_block.splitlines():
        line = raw_line.strip()
        if not line:
            if current_lines and current_lines[-1] != '':
                current_lines.append('')
            continue

        if _is_zhihu_answer_tail(line):
            break

        if avatar_pattern.match(line):
            continue

        author_match = author_pattern.match(line)
        if author_match:
            flush_answer()
            current_author = author_match.group(1).strip()
            continue

        if not current_author:
            continue

        current_lines.append(raw_line)

    flush_answer()

    if not answers:
        return {'success': False, 'error': '未提取到知乎公开回答'}

    parts = [f'# {title}', '', '## 回答', '']
    for index, answer in enumerate(answers, 1):
        parts.append(f'{index}. {answer["author"]}')
        parts.append(answer['body'])
        if index != len(answers):
            parts.append('')

    cleaned = '\n'.join(parts).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': title,
            'content_type': 'qa_answers',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _pick_x_title(markdown: str, metadata: dict) -> str:
    jina_title = metadata.get('jina_title', '')
    match = re.search(r'on (?:X|Twitter):\s*"(.*?)"\s*/\s*(?:X|Twitter)$', jina_title)
    if match:
        return match.group(1).strip()

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line or _is_x_noise(line) or _normalize_link_wrapped_image(line):
            continue
        cleaned = _clean_inline_markdown(line)
        if cleaned:
            return cleaned
    return 'untitled'


def _pick_zhihu_question_title(markdown: str, metadata: dict) -> str:
    title = extract_title(markdown)
    if title != 'untitled':
        return title
    raw_title = metadata.get('jina_title', '')
    return re.sub(r'\s*-\s*知乎$', '', raw_title).strip() or 'untitled'


def _pick_x_author(metadata: dict) -> str:
    jina_title = metadata.get('jina_title', '')
    match = re.match(r'(.+?) on (?:X|Twitter):', jina_title)
    if match:
        return match.group(1).strip()
    return ''


def _clean_nodeseek_body(text: str) -> str:
    lines: list[str] = []
    for raw_line in _truncate_nodeseek_tail(text).splitlines():
        line = raw_line.strip()
        if not line or _is_nodeseek_noise(line):
            if lines and lines[-1] != '':
                lines.append('')
            continue

        cleaned = _clean_inline_markdown(line)
        if cleaned:
            lines.append(cleaned)

    return _join_paragraphs(lines)


def _clean_zhihu_answer_body(lines: list[str]) -> str:
    kept: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            if kept and kept[-1] != '':
                kept.append('')
            continue
        if _is_zhihu_answer_noise(line):
            continue
        cleaned = _clean_inline_markdown(line)
        if cleaned:
            kept.append(cleaned)

    while kept and kept[-1] == '':
        kept.pop()

    non_empty = [line for line in kept if line]
    if len(non_empty) >= 2 and _looks_like_zhihu_bio_line(non_empty[0], non_empty[1]):
        drop_first = True
        trimmed: list[str] = []
        for line in kept:
            if drop_first and line == non_empty[0]:
                drop_first = False
                continue
            trimmed.append(line)
        kept = trimmed

    return _join_paragraphs(kept)


def _extract_vanilla_replies(comments_block: str) -> list[dict[str, str]]:
    if not comments_block.strip():
        return []

    comments_block = re.split(r'\n(?:\[Sign In\].*?to comment\.|#### Howdy, Stranger!|#### Categories|#### In this Discussion|© LowEndSpirit|Back to Top)', comments_block, 1, re.S)[0]
    pattern = re.compile(
        r'\*\s+\[!\[Image.*?\]\([^)]+\)\]\([^)]+\)\[(?P<user>[^\]]+)\]\([^)]+\)'
        r'(?P<role>[^\[]*?)\[(?P<time>[^\]]+)\]\([^)]+\)\s*(?P<body>.*?)(?='
        r'\n\*\s+\[!\[Image|\Z)',
        re.S,
    )
    replies: list[dict[str, str]] = []
    for match in pattern.finditer(comments_block):
        role = _clean_inline_markdown(match.group('role'))
        header = f'{match.group("user").strip()}'
        if role:
            header += f' | {role}'
        header += f' | {match.group("time").strip()}'

        body = match.group('body')
        body = re.sub(r'Thanked by.*', '', body, flags=re.S)
        cleaned = _clean_vanilla_body(body)
        if cleaned and _should_keep_reply(cleaned):
            replies.append({'header': header, 'body': cleaned})
    return replies


def _clean_vanilla_body(text: str) -> str:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or _is_vanilla_forum_noise(line):
            if lines and lines[-1] != '':
                lines.append('')
            continue
        cleaned = _clean_inline_markdown(line)
        if cleaned:
            lines.append(cleaned)
    return _join_paragraphs(lines)


def _clean_inline_markdown(text: str) -> str:
    text = re.sub(r'!\[.*?\]\([^)]+\)', '', text)
    text = re.sub(r'\[\]\([^)]+\)', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'^\s*>+\s*', '', text)
    text = re.sub(r'^\s*#{1,6}\s*', '', text)
    text = re.sub(r'^\s*[*+-]\s+', '', text)
    text = text.replace('`', '')
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    text = re.sub(r'(?<!\w)\*(.+?)\*(?!\w)', r'\1', text)
    text = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'\1', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip(' -·|')


def _normalize_link_wrapped_image(line: str) -> str:
    match = re.fullmatch(r'\[(!\[[^\]]*\]\((https?://[^)]+)\))\]\((https?://[^)]+)\)', line)
    if match:
        return match.group(1)
    return ''


def _should_keep_reply(text: str) -> bool:
    text = text.strip()
    if not text:
        return False
    if _is_low_value_reward_reply(text):
        return False
    if _has_reply_information_signal(text):
        return True
    if _is_emoji_or_punctuation_only(text):
        return False

    normalized = _normalize_reply_text(text)
    exact_noise = {
        'bd', 'dd', '顶', '帮顶', '支持', '前排', '路过', '围观', 'mark', '插眼',
        '好鸡', '好机', '实力', '厉害了', '牛逼', 'nb', '不错', '学习了',
    }
    if normalized in exact_noise:
        return False

    short_support_tokens = ('前排', '支持', '帮顶', '围观', '占领前排')
    short_praise_tokens = ('好鸡', '好机', '厉害', '实力', '不错', '牛', '牛逼', 'nb', '学习了')
    if len(text) <= 20 and any(token in text for token in short_support_tokens):
        return False
    if len(text) <= 12 and any(token in text for token in short_praise_tokens):
        return False
    return True


def _has_reply_information_signal(text: str) -> bool:
    lowered = text.lower()
    if any(token in text for token in ('?', '？', '吗', '怎么', '如何', '是否', '能否', '有没有', '实测')):
        return True
    if re.search(r'\d', text):
        return True
    if any(token in lowered for token in ('http://', 'https://', '.com', 'github', 'curl', 'bash', 'docker', 'tcp_', 'sysctl')):
        return True
    if any(token in text for token in ('配置', '参数', '版本', '测试', '日志', '报错', '解锁', '恢复', '定位', '命令', '脚本', '部署', '运行', '流量', '风险')):
        return True
    if len(text) > 24:
        return True
    return False


def _is_emoji_or_punctuation_only(text: str) -> bool:
    stripped = re.sub(r'[\s\W_]+', '', text, flags=re.UNICODE)
    return not stripped


def _normalize_reply_text(text: str) -> str:
    return re.sub(r'[\s\W_]+', '', text.lower(), flags=re.UNICODE)


def _is_low_value_reward_reply(text: str) -> bool:
    compact = re.sub(r'\s+', ' ', text.strip())
    lowered = compact.lower()
    thanks_tokens = ('谢谢老板', '多谢老板', '感谢老板', '老板大气', '谢谢', '多谢', '感谢')
    if re.fullmatch(r'(?:id[:：]?\s*)?\d{2,8}(?:[,，]\s*\d{2,8})*(?:\s*[,，]?\s*(谢谢老板|多谢老板|感谢老板|老板大气|谢谢|多谢|感谢))?[!！~～]*', compact, re.IGNORECASE):
        return True
    if re.fullmatch(r'(谢谢老板|多谢老板|感谢老板|老板大气)[!！~～]*', compact):
        return True
    if re.fullmatch(r'\d{2,8}', compact):
        return True
    if len(compact) <= 40 and re.search(r'\d{2,8}', compact) and any(token in lowered for token in ('id', '邀请码', 'invite')):
        return True
    if len(compact) <= 30 and re.search(r'\d{2,8}', compact) and any(token in compact for token in thanks_tokens):
        return True
    return False


def _looks_like_zhihu_bio_line(first_line: str, second_line: str) -> bool:
    if len(first_line) > 40:
        return False
    if len(second_line) < 20:
        return False
    if first_line.startswith(('1.', '2.', '3.', '#', '```', '>')):
        return False
    if re.search(r'https?://|www\.|vlink\.|公众号|全网同名|答主|欢迎关注', first_line):
        return True
    if len(first_line) <= 16:
        return True
    return False


def _truncate_nodeseek_tail(text: str) -> str:
    markers = (
        '\n[登录](',
        '\n#### 你好啊，陌生人!',
        '\n#### 快捷功能区',
        '\n#### 📈用户数目📈',
        '\n#### 🎉欢迎新用户🎉',
        '\n相关网站',
        '\n站内导航',
        '\n商业推广',
        '\n其他平台',
        '\n联系我们',
        '\n Copyright ©',
    )
    cut_points = [text.find(marker) for marker in markers if text.find(marker) != -1]
    if cut_points:
        return text[:min(cut_points)].rstrip()
    return text


def _truncate_linuxdo_tail(text: str) -> str:
    markers = (
        '\n### Related topics',
        '\n## Related topics',
    )
    cut_points = [text.find(marker) for marker in markers if text.find(marker) != -1]
    if cut_points:
        return text[:min(cut_points)].rstrip()
    return text


def _truncate_v2ex_tail(text: str) -> str:
    markers = (
        '\n通过 Atom Feed 订阅',
        '\n»More Recent Topics',
        '\n创建新节点浏览全部节点',
        '\nV2EX / Curated Nodes',
        '\nAbout·Help·Advertise',
    )
    cut_points = [text.find(marker) for marker in markers if text.find(marker) != -1]
    if cut_points:
        return text[:min(cut_points)].rstrip()
    return text


def _truncate_x_tail(text: str) -> str:
    markers = (
        '\n## Replies',
        '\n## Related Posts',
        '\n## Discover more',
        '\nSign up for X',
    )
    cut_points = [text.find(marker) for marker in markers if text.find(marker) != -1]
    if cut_points:
        return text[:min(cut_points)].rstrip()
    return text


def _is_zhihu_answer_tail(line: str) -> bool:
    if line.startswith('查看剩余 ') and '回答' in line:
        return True
    if line.startswith('下载知乎客户端'):
        return True
    if line.startswith('大家都在搜'):
        return True
    return False


def _is_x_noise(line: str) -> bool:
    lowered = line.lower()
    if line in {'## Article', '## Conversation'}:
        return True
    if lowered.startswith('listen to this article'):
        return True
    if lowered.startswith('sign up for x'):
        return True
    return False


def _is_nodeseek_noise(line: str) -> bool:
    lowered = line.lower()
    if line.startswith('**[![Image') or line.startswith('*   [日常]') or line.startswith('[search for'):
        return True
    if line.startswith('#### 所有版块') or line.startswith('NodeSeek beta'):
        return True
    if line.startswith('#### 你好啊，陌生人!') or line.startswith('#### 快捷功能区'):
        return True
    if line.startswith('#### 📈用户数目📈') or line.startswith('#### 🎉欢迎新用户🎉'):
        return True
    if line in {'你好啊，陌生人!', '快捷功能区', '推荐阅读'}:
        return True
    if line in {'相关网站', '站内导航', '商业推广', '其他平台', '联系我们'}:
        return True
    if 'all rights reserved' in lowered or '目前论坛共有' in line:
        return True
    if '登录' in line and '注册' in line and '评论' in line:
        return True
    if line.startswith('我的朋友，看起来你是新来的'):
        return True
    if re.fullmatch(r'\d+(?:\s+\d+)*', line):
        return True
    if re.fullmatch(r'\d+\[\d+\]\(\S+\)\[\]\(\S+\)', line):
        return True
    if line.startswith('[![') and 'favicon' in line:
        return True
    return False


def _is_zhihu_answer_noise(line: str) -> bool:
    lowered = line.lower()
    if line.startswith('![](<data:image'):
        return True
    if re.fullmatch(r'!\[[^\]]*\]\([^)]+\)', line):
        return True
    if line in {'关注者', '被浏览'}:
        return True
    if re.fullmatch(r'\*\*\d[\d,]*\*\*', line):
        return True
    if line.startswith('创建时间：') or line.startswith('最后编辑：'):
        return True
    if lowered.startswith('download zhihu app'):
        return True
    return False


def _is_v2ex_noise(line: str) -> bool:
    if line in {'[](javascript:)[](javascript:)', 'PRO'}:
        return True
    if line.startswith('[Home]') or line.startswith('如果想在 V2EX 获得更好的推广效果'):
        return True
    if line.startswith('Promoted by ') or line.startswith('[V2EX]') or line.startswith('[AI]'):
        return True
    return False


def _is_v2ex_reply_noise(line: str) -> bool:
    if line == '深入探索':
        return True
    if line.startswith('通过 Atom Feed 订阅') or line.startswith('»More Recent Topics'):
        return True
    if line.startswith('About·Help·Advertise'):
        return True
    if line in {
        'AI 代理服务', 'AI 编程工具', 'Mac OS', '操作系统', 'OS', '浏览器推荐',
        'GPT Plus 教程', '开源模型适配', '程序员社区', 'LLM 模型分享', '技术创意讨论',
        '编程语言', '智能手机', 'mac', 'macOS', '机器人学', '编程', '机器学习与人工智能',
        'AI 命令工具', 'AI 编程方案',
    }:
        return True
    if line.startswith('Supplement ') or re.fullmatch(r'!\[Image \d+\]\(https?://i\.v2ex\.co/[^)]+\)', line):
        return True
    return False


def _clean_linuxdo_body(text: str) -> str:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if lines and lines[-1] != '':
                lines.append('')
            continue
        if line == 'Solution':
            continue
        if re.fullmatch(r'\[!\[Image .*?\]\([^)]+\)\]\([^)]+\)', line):
            continue
        cleaned = _clean_inline_markdown(line)
        if cleaned:
            lines.append(cleaned)
    return _join_paragraphs(lines)


def _extract_v2ex_replies(text: str) -> list[dict[str, str]]:
    replies: list[dict[str, str]] = []
    if not text.strip():
        return replies

    image_floor_pattern = re.compile(r'^!\[Image.*?\]\([^)]+\)(?P<floor>\d+)$')
    user_time_pattern = re.compile(r'^\*\*\[(?P<user>[^\]]+)\]\(https://www\.v2ex\.com/member/[^)]+\)\*\*(?P<time>.+)$')
    skip_until_next_floor = False

    current_header = ''
    current_floor = ''
    current_lines: list[str] = []

    def flush_current() -> None:
        nonlocal current_header, current_floor, current_lines
        if not current_header:
            current_lines = []
            return
        body = _clean_v2ex_reply_body('\n'.join(current_lines))
        if _should_keep_reply(body):
            header = current_header
            if current_floor:
                header = f'{header} | #{current_floor}'
            replies.append({'header': header, 'body': body or '(无正文)'})
        current_header = ''
        current_floor = ''
        current_lines = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if current_lines and current_lines[-1] != '':
                current_lines.append('')
            continue
        floor_match = image_floor_pattern.match(line)
        if floor_match:
            skip_until_next_floor = False
            flush_current()
            current_floor = floor_match.group('floor')
            continue
        if skip_until_next_floor:
            continue
        if _is_v2ex_reply_noise(line):
            flush_current()
            skip_until_next_floor = True
            continue
        if _is_v2ex_noise(line):
            continue
        header_match = user_time_pattern.match(line)
        if header_match:
            current_header = f'{header_match.group("user").strip()} | {header_match.group("time").strip()}'
            continue
        if current_header:
            current_lines.append(raw_line)

    flush_current()
    return replies


def _clean_v2ex_reply_body(text: str) -> str:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if lines and lines[-1] != '':
                lines.append('')
            continue
        if re.fullmatch(r'\d{2,8}', line):
            lines.append(line)
            continue
        cleaned = _clean_inline_markdown(line)
        if cleaned:
            lines.append(cleaned)
    return _join_paragraphs(lines)
def _is_vanilla_forum_noise(line: str) -> bool:
    lowered = line.lower()
    if line.startswith('toggle menu') or line == '×':
        return True
    if line.startswith('[Categories]') or line.startswith('[Discussions]') or line.startswith('[Support]'):
        return True
    if line.startswith('[About]') or line.startswith('[Rules]') or line.startswith('[Sign In]'):
        return True
    if line.startswith('[Home]') or line.startswith('**[LowEndTalk]'):
        return True
    if line.startswith('#### Howdy, Stranger!') or line.startswith('## Quick Links'):
        return True
    if 'register' in lowered and 'sign in' in lowered:
        return True
    if 'lowendspirit.com/uploads/' in lowered or 'lowendtalk.com/uploads/editor/' in lowered:
        return True
    if line.startswith('© LowEndSpirit') or line.startswith('*   2008-2025 ©'):
        return True
    if re.fullmatch(r'[«\[\]\(\)\d/p .]+', line):
        return True
    return False


def _join_paragraphs(lines: list[str]) -> str:
    text = '\n'.join(lines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
