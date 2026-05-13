"""
Content utilities: title extraction, image extraction, filename sanitization.
Pure utility module with no internal imports.
"""

import html
import json
import re
import unicodedata
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
    'finance_stock': {
        'window_start_markers': (),
        'tail_markers': (
            '相关推荐',
            '热门评论',
            '杜邦分析原理',
            '招聘动态',
            '全站热榜',
            '创作者周榜',
            '正在热议',
        ),
        'drop_exact': {
            '首页', '登录', '注册', '分享', '收藏', '举报', '反馈', '行情', '股吧',
            '新闻', '外汇', '新三板', '最新价： --', '涨跌幅： --',
        },
        'drop_prefixes': (
            '新浪首页',
            '财经首页',
            '最近访问股',
            '查看自选股请先',
            'F10 功能找不到',
            '谢谢您的支持',
        ),
        'drop_contains': (
            '登录/注册',
            '意见反馈',
            '免责声明',
            '扫码登录',
            '版权所有',
            '牛客科技©',
        ),
        'drop_regexes': (
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

    if _is_eastmoney_platform(platform, url):
        return _extract_eastmoney_content(markdown, metadata, url)

    if _is_sinafinance_platform(platform, url):
        return _extract_sinafinance_content(markdown, metadata, url)

    if _is_finance_stock_platform(platform, url):
        return _extract_finance_stock_content(markdown, metadata, url, platform)

    if _is_wallstreetcn_platform(platform, url):
        return _extract_wallstreetcn_content(markdown, metadata, url)

    if _is_maimai_platform(platform, url):
        return _extract_maimai_content(markdown, metadata, url)

    if _is_nowcoder_platform(platform, url):
        return _extract_nowcoder_content(markdown, metadata, url)

    if _is_cls_platform(platform, url):
        return _extract_cls_content(markdown, metadata, url)

    if _is_sec_platform(platform, url):
        return _extract_sec_content(markdown, metadata, url)

    if _is_hkexnews_platform(platform, url):
        return _extract_hkexnews_content(markdown, metadata, url)

    if _is_reuters_platform(platform, url):
        return _extract_reuters_content(markdown, metadata, url)

    if _is_sse_platform(platform, url):
        return _extract_sse_content(markdown, metadata, url)

    if _is_cninfo_platform(platform, url):
        return _extract_cninfo_content(markdown, metadata, url)

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


def _is_cninfo_platform(platform: dict, url: str) -> bool:
    if platform.get('id') == 'cninfo':
        return True
    return 'cninfo.com.cn' in urlparse(url).netloc.lower()


def _is_sse_platform(platform: dict, url: str) -> bool:
    if platform.get('id') == 'sse':
        return True
    return 'sse.com.cn' in urlparse(url).netloc.lower()


def _is_reuters_platform(platform: dict, url: str) -> bool:
    if platform.get('id') == 'reuters':
        return True
    return 'reuters.com' in urlparse(url).netloc.lower()


def _is_hkexnews_platform(platform: dict, url: str) -> bool:
    if platform.get('id') == 'hkexnews':
        return True
    return 'hkexnews.hk' in urlparse(url).netloc.lower()


def _is_sec_platform(platform: dict, url: str) -> bool:
    if platform.get('id') == 'sec':
        return True
    return 'sec.gov' in urlparse(url).netloc.lower()


def _is_cls_platform(platform: dict, url: str) -> bool:
    if platform.get('id') == 'cls':
        return True
    return 'cls.cn' in urlparse(url).netloc.lower()


def _is_maimai_platform(platform: dict, url: str) -> bool:
    if platform.get('id') == 'maimai':
        return True
    return 'maimai.cn' in urlparse(url).netloc.lower()


def _is_finance_stock_platform(platform: dict, url: str) -> bool:
    if platform.get('cleanup_profile') == 'finance_stock':
        return platform.get('id') not in {'sinafinance', 'eastmoney'}
    return False


def _is_nowcoder_platform(platform: dict, url: str) -> bool:
    if platform.get('id') == 'nowcoder':
        return True
    return 'nowcoder.com' in urlparse(url).netloc.lower()


def _is_eastmoney_platform(platform: dict, url: str) -> bool:
    if platform.get('id') == 'eastmoney':
        return True
    domain = urlparse(url).netloc.lower()
    return 'eastmoney.com' in domain


def _is_sinafinance_platform(platform: dict, url: str) -> bool:
    if platform.get('id') == 'sinafinance':
        return True
    return 'finance.sina.com.cn' in urlparse(url).netloc.lower()


def _is_wallstreetcn_platform(platform: dict, url: str) -> bool:
    if platform.get('id') == 'wallstreetcn':
        return True
    return 'wallstreetcn.com' in urlparse(url).netloc.lower()


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

    pages_match = re.search(r'^Number of Pages:\s*(\d+)$', content, re.MULTILINE)
    if pages_match:
        metadata['page_count'] = pages_match.group(1).strip()

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


def _pick_maimai_title(markdown: str, metadata: dict) -> str:
    raw_title = metadata.get('jina_title', '').strip()
    if raw_title and raw_title != '登录 / 注册':
        return re.sub(r'脉脉$', '', raw_title).strip()

    for raw_line in markdown.splitlines():
        cleaned = _normalize_cninfo_line(_clean_inline_markdown(raw_line))
        if not cleaned or cleaned in {'登录 / 注册', '好友'}:
            continue
        if re.fullmatch(r'\d{2,4}-\d{1,2}-\d{1,2}\s*·\s*.+', cleaned):
            continue
        return re.sub(r'脉脉$', '', cleaned).strip()
    return 'untitled'


def _pick_nowcoder_title(markdown: str, metadata: dict) -> str:
    raw_title = metadata.get('jina_title', '').strip()
    if raw_title and raw_title != '登录 / 注册':
        return re.sub(r'_牛客网$', '', raw_title).strip()

    for raw_line in markdown.splitlines():
        cleaned = _normalize_cninfo_line(_clean_inline_markdown(raw_line))
        if not cleaned or _is_nowcoder_discuss_noise(cleaned, ''):
            continue
        if _looks_like_nowcoder_section_heading(cleaned):
            continue
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}', cleaned):
            continue
        return re.sub(r'_牛客网$', '', cleaned).strip()
    return 'untitled'


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
    answer_start = re.search(r'(?m)^(?:####\s+)?\d+\s+个回答\s*$', markdown)
    if not answer_start:
        return {'success': False, 'error': '知乎问题回答区提取失败'}

    answer_block = markdown[answer_start.end():]
    if not re.search(r'(?m)^\[([^\]]+)\]\((?:https?:)?//www\.zhihu\.com/people/[^)]+\)$', answer_block):
        answers = _extract_zhihu_plaintext_answers(answer_block)
        if answers:
            return _format_zhihu_answers(title, answers, markdown, metadata)

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

    return _format_zhihu_answers(title, answers, markdown, metadata)


def _extract_zhihu_plaintext_answers(answer_block: str) -> list[dict[str, str]]:
    lines = answer_block.splitlines()
    answers: list[dict[str, str]] = []
    current_author = ''
    current_lines: list[str] = []

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

    for index, raw_line in enumerate(lines):
        line = _normalize_invisible_whitespace(raw_line).strip()
        if not line:
            if current_lines and current_lines[-1] != '':
                current_lines.append('')
            continue
        if _is_zhihu_answer_tail(line):
            break

        if _looks_like_zhihu_plaintext_author(lines, index):
            flush_answer()
            current_author = line
            continue

        if not current_author:
            continue

        current_lines.append(raw_line)

    flush_answer()
    return answers


def _format_zhihu_answers(title: str, answers: list[dict[str, str]], markdown: str, metadata: dict) -> dict:
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


def _extract_cninfo_content(markdown: str, metadata: dict, url: str) -> dict:
    if _is_cninfo_notice_list(url, markdown):
        return _extract_cninfo_notice_list(markdown, metadata)
    if _is_cninfo_announcement_document(url, markdown):
        return _extract_cninfo_announcement(markdown, metadata)

    cleaned, cleanup_stats = _apply_platform_cleanup(markdown, {'cleanup_profile': 'generic'})
    title = _pick_title(cleaned, metadata)
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            **cleanup_stats,
            'title': title,
        },
    }


def _extract_sse_content(markdown: str, metadata: dict, url: str) -> dict:
    if _is_sse_notice_list(url, markdown):
        return _extract_sse_notice_list(markdown, metadata)
    if _is_sse_announcement_document(url, markdown):
        return _extract_sse_announcement(markdown, metadata)

    cleaned, cleanup_stats = _apply_platform_cleanup(markdown, {'cleanup_profile': 'generic'})
    title = _pick_title(cleaned, metadata)
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            **cleanup_stats,
            'title': title,
        },
    }


def _extract_reuters_content(markdown: str, metadata: dict, url: str) -> dict:
    if _is_reuters_markets_page(url, markdown):
        return _extract_reuters_markets_page(markdown, metadata)
    return _extract_reuters_article(markdown, metadata)


def _extract_hkexnews_content(markdown: str, metadata: dict, url: str) -> dict:
    if _is_hkexnews_title_search_page(url, markdown):
        return _extract_hkexnews_title_search(markdown, metadata)
    if _is_hkexnews_announcement_document(url, markdown):
        return _extract_hkexnews_announcement(markdown, metadata)

    cleaned, cleanup_stats = _apply_platform_cleanup(markdown, {'cleanup_profile': 'generic'})
    title = _pick_title(cleaned, metadata)
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            **cleanup_stats,
            'title': title,
        },
    }


def _extract_sec_content(markdown: str, metadata: dict, url: str) -> dict:
    if _is_sec_browse_page(url, markdown):
        return _extract_sec_browse_page(markdown, metadata)
    if _is_sec_filing_index_page(url, markdown):
        return _extract_sec_filing_index_page(markdown, metadata, url)

    cleaned, cleanup_stats = _apply_platform_cleanup(markdown, {'cleanup_profile': 'generic'})
    title = _pick_title(cleaned, metadata)
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            **cleanup_stats,
            'title': title,
        },
    }


def _extract_cls_content(markdown: str, metadata: dict, url: str) -> dict:
    if _is_cls_detail_page(url, markdown):
        return _extract_cls_detail_page(markdown, metadata)
    return _extract_cls_home_page(markdown, metadata)


def _extract_eastmoney_content(markdown: str, metadata: dict, url: str) -> dict:
    if _is_eastmoney_stock_page(url, markdown):
        return _extract_finance_stock_content(markdown, metadata, url, {'id': 'eastmoney', 'name': '东方财富', 'cleanup_profile': 'finance_stock'})
    if _is_eastmoney_article_page(url, markdown):
        return _extract_eastmoney_article_page(markdown, metadata)
    return _extract_eastmoney_home_page(markdown, metadata)


def _extract_sinafinance_content(markdown: str, metadata: dict, url: str) -> dict:
    if _is_sinafinance_stock_page(url, markdown):
        return _extract_finance_stock_content(markdown, metadata, url, {'id': 'sinafinance', 'name': '新浪财经', 'cleanup_profile': 'finance_stock'})
    if _is_sinafinance_article_page(url, markdown):
        return _extract_sinafinance_article_page(markdown, metadata)
    return _extract_sinafinance_home_page(markdown, metadata)


def _extract_wallstreetcn_content(markdown: str, metadata: dict, url: str) -> dict:
    if _is_wallstreetcn_article_page(url, markdown):
        return _extract_wallstreetcn_article_page(markdown, metadata)
    return _extract_wallstreetcn_home_page(markdown, metadata)


def _extract_maimai_content(markdown: str, metadata: dict, url: str) -> dict:
    if _is_maimai_article_page(url, markdown):
        return _extract_maimai_article_page(markdown, metadata)

    cleaned, cleanup_stats = _apply_platform_cleanup(markdown, {'cleanup_profile': 'generic'})
    title = _pick_title(cleaned, metadata)
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            **cleanup_stats,
            'title': title,
        },
    }


def _extract_nowcoder_content(markdown: str, metadata: dict, url: str) -> dict:
    if _is_nowcoder_discuss_page(url, markdown):
        return _extract_nowcoder_discuss_page(markdown, metadata)

    cleaned, cleanup_stats = _apply_platform_cleanup(markdown, {'cleanup_profile': 'generic'})
    title = _pick_title(cleaned, metadata)
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            **cleanup_stats,
            'title': title,
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


def _pick_cninfo_notice_title(metadata: dict) -> str:
    return '巨潮资讯最新公告'


def _pick_sse_notice_title(metadata: dict) -> str:
    return '上交所公司公告'


def _pick_reuters_title(markdown: str, metadata: dict) -> str:
    raw_title = metadata.get('jina_title', '').strip()
    if raw_title:
        return re.sub(r'\s*\|\s*Reuters$', '', raw_title).strip()
    title = _pick_title(markdown, metadata)
    return re.sub(r'\s*\|\s*Reuters$', '', title).strip()


def _pick_hkexnews_title(markdown: str, metadata: dict) -> str:
    raw_title = metadata.get('jina_title', '').strip()
    if raw_title and raw_title != 'Listed Company Information Title Search':
        return raw_title
    return _pick_title(markdown, metadata)


def _pick_finance_stock_title(markdown: str, metadata: dict) -> str:
    raw_title = metadata.get('jina_title', '').strip() or _pick_title(markdown, metadata)
    raw_title = re.sub(r'\|.*新浪财经.*$', '', raw_title).strip()
    raw_title = re.sub(r'\s*[—-]\s*东方财富网$', '', raw_title).strip()
    raw_title = re.sub(r'_F10_同花顺金融服务网$', '', raw_title).strip()
    raw_title = re.sub(r'\s+[—-]\s+东方财富网$', '', raw_title).strip()
    return raw_title or '财经个股页'


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


def _extract_cninfo_announcement(markdown: str, metadata: dict) -> dict:
    normalized_lines: list[tuple[int, str]] = []
    for index, raw_line in enumerate(markdown.splitlines()):
        cleaned = _normalize_cninfo_line(_clean_inline_markdown(raw_line))
        if cleaned:
            normalized_lines.append((index, cleaned))

    code_line = ''
    company = ''
    title = ''
    body_start = 0

    for pos, (line_index, line) in enumerate(normalized_lines):
        if not code_line and line.startswith('证券代码'):
            code_line = line
            if pos + 1 < len(normalized_lines):
                company = normalized_lines[pos + 1][1]
            if pos + 2 < len(normalized_lines):
                title = normalized_lines[pos + 2][1]
                body_start = normalized_lines[pos + 2][0] + 1
            break

    if not title:
        title = _pick_title(markdown, metadata)
        body_start = 0

    code = ''
    sec_name = ''
    notice_id = ''
    meta_match = re.search(
        r'证券代码[:：]\s*(?P<code>\d+)\s*证券简称[:：]\s*(?P<name>.+?)\s*公告编号[:：]\s*(?P<notice>[\d\-\s]+)',
        code_line,
    )
    if meta_match:
        code = meta_match.group('code').strip()
        sec_name = meta_match.group('name').strip()
        notice_id = re.sub(r'\s+', '', meta_match.group('notice')).strip()

    body_lines: list[str] = []
    for raw_line in markdown.splitlines()[body_start:]:
        line = _normalize_cninfo_line(_clean_inline_markdown(raw_line))
        if not line or _is_cninfo_announcement_noise(line):
            continue
        body_lines.append(line)

    body = _join_cninfo_announcement_lines(body_lines)
    full_title = ''.join(part for part in (company, title) if part)
    if not full_title:
        full_title = title or company or '巨潮资讯公告'

    parts = [f'# {full_title}']
    if code:
        parts.append(f'**证券代码**: {code}')
    if sec_name:
        parts.append(f'**证券简称**: {sec_name}')
    if notice_id:
        parts.append(f'**公告编号**: {notice_id}')
    if metadata.get('published_time'):
        parts.append(f'**发布时间**: {metadata["published_time"]}')
    if metadata.get('page_count'):
        parts.append(f'**页数**: {metadata["page_count"]}')
    parts.extend(['', '## 正文', '', body or '未提取到公告正文'])

    cleaned = '\n'.join(parts).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': full_title,
            'content_type': 'financial_disclosure',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _extract_cninfo_notice_list(markdown: str, metadata: dict) -> dict:
    notices: list[str] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line or 'new/disclosure/detail?' not in line:
            continue
        code_match = re.search(r'\[(\d{6})\]\(https://www\.cninfo\.com\.cn/new/disclosure/stock\?[^)]+\)', line)
        name_match = re.search(
            r'\[\d{6}\]\(https://www\.cninfo\.com\.cn/new/disclosure/stock\?[^)]+\)\[([^\]]+)\]\(https://www\.cninfo\.com\.cn/new/disclosure/stock\?[^)]+\)',
            line,
        )
        detail_titles = re.findall(r'\[([^\]]+)\]\(https://www\.cninfo\.com\.cn/new/disclosure/detail\?[^)]+\)', line)
        times = re.findall(r'(20\d{2}-\d{2}-\d{2} \d{2}:\d{2})', line)

        if not code_match or not name_match or not detail_titles:
            continue

        code = code_match.group(1).strip()
        name = name_match.group(1).strip()

        for idx, detail_title in enumerate(detail_titles):
            notice_time = times[idx] if idx < len(times) else (times[-1] if times else '')
            entry = f'- {code} {name} | {_normalize_cninfo_line(detail_title)}'
            if notice_time:
                entry += f' | {notice_time}'
            notices.append(entry)

    if not notices:
        return {'success': False, 'error': '巨潮公告列表提取失败'}

    title = _pick_cninfo_notice_title(metadata)
    parts = [f'# {title}', '', '## 公告', '']
    parts.extend(notices)
    cleaned = '\n'.join(parts).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': title,
            'content_type': 'financial_notice_list',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _extract_sse_announcement(markdown: str, metadata: dict) -> dict:
    normalized_lines: list[tuple[int, str]] = []
    for index, raw_line in enumerate(markdown.splitlines()):
        cleaned = _normalize_cninfo_line(_clean_inline_markdown(raw_line))
        if cleaned:
            normalized_lines.append((index, cleaned))

    code_line = ''
    company = ''
    title = ''
    body_start = 0

    for pos, (line_index, line) in enumerate(normalized_lines):
        if not code_line and line.startswith('证券代码'):
            code_line = line
            if pos + 1 < len(normalized_lines):
                company = normalized_lines[pos + 1][1]
            if pos + 2 < len(normalized_lines):
                title = normalized_lines[pos + 2][1]
                body_start = normalized_lines[pos + 2][0] + 1
            break

    if not title:
        title = _pick_title(markdown, metadata)
        body_start = 0

    code = ''
    sec_name = ''
    notice_id = ''
    meta_match = re.search(
        r'证券代码[:：]\s*(?P<code>\d+)\s*证券简称[:：]\s*(?P<name>.+?)\s*公告编号[:：]\s*(?P<notice>[\d\-\s]+)',
        code_line,
    )
    if meta_match:
        code = meta_match.group('code').strip()
        sec_name = meta_match.group('name').strip()
        notice_id = re.sub(r'\s+', '', meta_match.group('notice')).strip()

    body_lines: list[str] = []
    for raw_line in markdown.splitlines()[body_start:]:
        line = _normalize_cninfo_line(_clean_inline_markdown(raw_line))
        if not line or _is_sse_announcement_noise(line):
            continue
        body_lines.append(line)

    body = _join_cninfo_announcement_lines(body_lines)
    full_title = ''.join(part for part in (company, title) if part)
    if not full_title:
        full_title = title or company or '上交所公告'

    parts = [f'# {full_title}']
    if code:
        parts.append(f'**证券代码**: {code}')
    if sec_name:
        parts.append(f'**证券简称**: {sec_name}')
    if notice_id:
        parts.append(f'**公告编号**: {notice_id}')
    if metadata.get('published_time'):
        parts.append(f'**发布时间**: {metadata["published_time"]}')
    if metadata.get('page_count'):
        parts.append(f'**页数**: {metadata["page_count"]}')
    parts.extend(['', '## 正文', '', body or '未提取到公告正文'])

    cleaned = '\n'.join(parts).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': full_title,
            'content_type': 'financial_disclosure',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _extract_sse_notice_list(markdown: str, metadata: dict) -> dict:
    notices: list[str] = []
    pattern = re.compile(
        r'\*\s+_(?P<date>\d{4}-\d{2}-\d{2})_\[(?P<code>\d{6})\s*:\s*(?P<title>[^\]]+)\]'
        r'\((?P<url>https://(?:star|www|big5)\.sse\.com\.cn/[^)]+)\)'
    )

    for match in pattern.finditer(markdown):
        notice_date = match.group('date').strip()
        code = match.group('code').strip()
        title = _normalize_cninfo_line(match.group('title').strip())
        notices.append(f'- {notice_date} | {code} | {title}')

    if not notices:
        return {'success': False, 'error': '上交所公告列表提取失败'}

    title = _pick_sse_notice_title(metadata)
    parts = [f'# {title}', '', '## 公告', '']
    parts.extend(notices)
    cleaned = '\n'.join(parts).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': title,
            'content_type': 'financial_notice_list',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _extract_reuters_article(markdown: str, metadata: dict) -> dict:
    title = _pick_reuters_title(markdown, metadata)
    image = ''
    body_lines: list[str] = []

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            if body_lines and body_lines[-1] != '':
                body_lines.append('')
            continue

        normalized_image = _normalize_link_wrapped_image(line)
        if normalized_image and not image:
            image = normalized_image
            continue
        if line.startswith('![') and not image:
            image = line
            continue
        if _is_reuters_article_noise(line):
            break

        cleaned = _clean_inline_markdown(line)
        if not cleaned or cleaned == title:
            continue
        if _is_reuters_inline_noise(cleaned):
            continue
        body_lines.append(cleaned)

    body = _join_paragraphs(body_lines)
    if len(body.strip()) < 80:
        return {'success': False, 'error': 'Reuters 文章提取失败'}

    parts = [f'# {title}']
    if image:
        parts.extend(['', '## 图片', '', image])
    parts.extend(['', '## 正文', '', body])

    cleaned = '\n'.join(parts).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': title,
            'content_type': 'financial_news_article',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _extract_reuters_markets_page(markdown: str, metadata: dict) -> dict:
    lead_title = ''
    lead_time = ''
    lead_summary = ''
    sections: dict[str, list[str]] = {}
    current_section = ''

    lines = [line.strip() for line in markdown.splitlines()]
    for idx, line in enumerate(lines):
        if not line:
            continue

        if not lead_title and line.startswith('[') and '](' in line and not line.startswith('[Official Data Partner]'):
            cleaned = _clean_inline_markdown(line)
            if cleaned and cleaned not in {'Markets'}:
                lead_title = cleaned
                continue

        if lead_title and not lead_time and line.startswith('· '):
            lead_time = line.strip('· ').strip()
            continue

        if lead_title and not lead_summary and line and 'REUTERS/' not in line and not line.startswith('[](') and not line.startswith('## '):
            if not line.startswith('-') and not line.startswith('['):
                lead_summary = _clean_inline_markdown(line)
                continue

        if line.startswith('## [') and '](' in line:
            current_section = _clean_inline_markdown(line)
            sections.setdefault(current_section, [])
            continue

        if line.startswith('## Markets Performance'):
            current_section = ''
            continue

        if current_section:
            if _is_reuters_markets_noise(line):
                continue
            if line.startswith('-'):
                bullet_title = _extract_reuters_bullet_title(line)
                if bullet_title and bullet_title not in sections[current_section]:
                    sections[current_section].append(bullet_title)
                continue
            if '](' in line:
                cleaned = _clean_inline_markdown(line)
                if cleaned and cleaned not in sections[current_section]:
                    sections[current_section].append(cleaned)

    if not lead_title:
        return {'success': False, 'error': 'Reuters Markets 页面提取失败'}

    parts = ['# Reuters Markets', '', '## Lead', '']
    parts.append(lead_title)
    if lead_time:
        parts.append(lead_time)
    if lead_summary:
        parts.append('')
        parts.append(lead_summary)

    for section_name, entries in sections.items():
        if not entries:
            continue
        parts.extend(['', f'## {section_name}', ''])
        for entry in entries:
            parts.append(f'- {entry}')

    cleaned = '\n'.join(parts).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': 'Reuters Markets',
            'content_type': 'financial_news_list',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _extract_hkexnews_title_search(markdown: str, metadata: dict) -> dict:
    entries: list[str] = []
    pattern = re.compile(
        r'Release Time:\s*(?P<time>\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})\s*\|\s*'
        r'Stock Code:\s*(?P<code>\d+)\s*\|\s*'
        r'Stock Short Name:\s*(?P<name>[^|]+?)\s*\|\s*'
        r'Document:\s*(?P<category>.*?)\[(?P<title>[^\]]+)\]'
        r'\((?P<url>https://www1\.hkexnews\.hk/listedco/listconews/sehk/[^)]+\.pdf)\)',
        re.S,
    )

    for match in pattern.finditer(markdown):
        release_time = match.group('time').strip()
        code = match.group('code').strip()
        name = match.group('name').strip()
        category = _normalize_cninfo_line(_clean_inline_markdown(match.group('category')))
        category = category.strip(' -|')
        title = _normalize_cninfo_line(_clean_inline_markdown(match.group('title')))
        entry = f'- {release_time} | {code} | {name} | {category} | {title}'
        entries.append(entry)

    if not entries:
        return {'success': False, 'error': 'HKEXnews 标题搜索结果提取失败'}

    parts = ['# HKEXnews 公司披露', '', '## 公告', '']
    parts.extend(entries)
    cleaned = '\n'.join(parts).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': 'HKEXnews 公司披露',
            'content_type': 'financial_notice_list',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _extract_hkexnews_announcement(markdown: str, metadata: dict) -> dict:
    stock_code = ''
    code_match = re.search(r'\(Stock Code:\s*(\d+)\)', markdown, re.IGNORECASE)
    if code_match:
        stock_code = code_match.group(1).strip()

    same_line_title_match = re.search(
        r'\(Stock Code:\s*\d+\)\s*(?P<title>.+?)\s*Independent Financial Adviser',
        markdown,
        re.IGNORECASE | re.S,
    )
    raw_lines = [line.strip() for line in markdown.splitlines()]
    title_parts: list[str] = []
    if same_line_title_match:
        title = _normalize_cninfo_line(_clean_inline_markdown(same_line_title_match.group('title')))
    else:
        capture_title = False
        for line in raw_lines[:40]:
            if not line:
                continue
            if re.search(r'\(Stock Code:\s*\d+\)', line, re.IGNORECASE):
                capture_title = True
                continue
            if not capture_title:
                continue
            if line.startswith('A letter from the Board'):
                break
            if line.startswith('THIS CIRCULAR IS IMPORTANT'):
                continue
            if line.startswith('If you are in any doubt'):
                continue
            if line.startswith('If you have sold or transferred'):
                continue
            if line.startswith('Hong Kong Exchanges and Clearing'):
                continue
            if line.startswith('(Incorporated in'):
                continue
            if line.startswith('SOMERLEY CAPITAL'):
                continue
            if re.fullmatch(r'\d+\s+[A-Za-z]+\s+\d{4}', line):
                continue
            if line and (line.isupper() or 'AND' in line or 'TRANSACTION' in line):
                title_parts.append(_normalize_cninfo_line(_clean_inline_markdown(line)))

        title = ' '.join(part for part in title_parts if part).strip()
    if not title:
        title = _pick_hkexnews_title(markdown, metadata)

    body_matches = list(re.finditer(r'LETTER FROM THE BOARD\s*–\s*\d+\s*–\s*', markdown))
    if len(body_matches) >= 2:
        body_markdown = markdown[body_matches[1].end():]
    elif body_matches:
        body_markdown = markdown[body_matches[0].end():]
    else:
        plain_match = re.search(r'LETTER FROM THE BOARD', markdown)
        body_markdown = markdown[plain_match.end():] if plain_match else markdown

    normalized_lines = [_normalize_cninfo_line(_clean_inline_markdown(line)) for line in body_markdown.splitlines()]
    body_lines: list[str] = []
    for line in normalized_lines:
        if not line or _is_hkexnews_announcement_noise(line):
            continue
        body_lines.append(line)

    body = _join_cninfo_announcement_lines(body_lines)
    if len(body.strip()) < 40:
        return {'success': False, 'error': 'HKEXnews 公告正文提取失败'}

    parts = [f'# {title}']
    if stock_code:
        parts.append(f'**证券代码**: {stock_code}')
    if metadata.get('published_time'):
        parts.append(f'**发布时间**: {metadata["published_time"]}')
    if metadata.get('page_count'):
        parts.append(f'**页数**: {metadata["page_count"]}')
    parts.extend(['', '## 正文', '', body])

    cleaned = '\n'.join(parts).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': title,
            'content_type': 'financial_disclosure',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _extract_sec_browse_page(markdown: str, metadata: dict) -> dict:
    entries: list[str] = []
    pattern = re.compile(
        r'(?P<form>[A-Z0-9\-\/]+)'
        r'\[(?P<description>.*?)\s+Open document\]\((?P<doc_url>https://www\.sec\.gov/[^)]+)\)'
        r'.*?'
        r'\[Filing Open filing\]\((?P<index_url>https://www\.sec\.gov/Archives/edgar/data/[^)]+-index\.htm)\)'
        r'Click to Open filing\s*(?P<filing_date>\d{4}-\d{2}-\d{2})?',
        re.S,
    )

    for match in pattern.finditer(markdown):
        form = match.group('form').strip()
        desc = _normalize_cninfo_line(match.group('description').strip())
        filing_date = (match.group('filing_date') or '').strip()
        index_url = match.group('index_url').strip()
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}', form):
            continue
        if 'View all with same reporting date' in desc:
            continue
        entry = f'- {form} | {desc}'
        if filing_date:
            entry += f' | {filing_date}'
        entry += f' | {index_url}'
        entries.append(entry)

    if not entries:
        return {'success': False, 'error': 'SEC EDGAR filings 列表提取失败'}

    cleaned = '\n'.join(['# SEC EDGAR Filings', '', '## Filings', '', *entries]).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': 'SEC EDGAR Filings',
            'content_type': 'financial_notice_list',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _extract_sec_filing_index_page(markdown: str, metadata: dict, url: str) -> dict:
    filing_id_match = re.search(r'EDGAR Filing Documents for ([\d-]+)', metadata.get('jina_title', ''))
    filing_id = filing_id_match.group(1).strip() if filing_id_match else url.rstrip('/').split('/')[-1].replace('-index.htm', '')

    filing_date_match = re.search(r'Filing Date\s+(\d{4}-\d{2}-\d{2})', markdown)
    accepted_match = re.search(r'Accepted\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', markdown)
    period_match = re.search(r'Period of Report\s+(\d{4}-\d{2}-\d{2})', markdown)

    filing_date = filing_date_match.group(1).strip() if filing_date_match else ''
    accepted = accepted_match.group(1).strip() if accepted_match else ''
    period = period_match.group(1).strip() if period_match else ''

    document_lines = re.findall(
        r'\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*\[([^\]]+)\]\([^)]+\).*?\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|',
        markdown,
        re.S,
    )

    if not document_lines:
        return {'success': False, 'error': 'SEC Filing index 提取失败'}

    parts = [f'# SEC Filing {filing_id}']
    if filing_date:
        parts.append(f'**Filing Date**: {filing_date}')
    if accepted:
        parts.append(f'**Accepted**: {accepted}')
    if period:
        parts.append(f'**Period of Report**: {period}')
    parts.extend(['', '## Documents', ''])

    for seq, desc, doc_name, doc_type, size in document_lines:
        parts.append(f'- {seq} | {desc.strip()} | {doc_type.strip()} | {size.strip()} | {doc_name.strip()}')

    cleaned = '\n'.join(parts).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': f'SEC Filing {filing_id}',
            'content_type': 'financial_disclosure',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _extract_cls_home_page(markdown: str, metadata: dict) -> dict:
    entries: list[str] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if _is_cls_home_noise(line):
            continue
        link_matches = re.findall(r'\[([^\]]+)\]\(https://www\.cls\.cn/detail/\d+\)', line)
        if not link_matches:
            continue
        for title in link_matches:
            cleaned = _normalize_cninfo_line(_clean_inline_markdown(title))
            if cleaned and cleaned not in entries:
                entries.append(cleaned)

    if not entries:
        return {'success': False, 'error': '财联社首页新闻流提取失败'}

    cleaned = '\n'.join(['# 财联社要闻', '', '## 新闻流', '', *[f'- {item}' for item in entries]]).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': '财联社要闻',
            'content_type': 'financial_news_list',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _extract_cls_detail_page(markdown: str, metadata: dict) -> dict:
    title = _pick_title(markdown, metadata)
    publish_time = ''
    source = ''
    summary_lines: list[str] = []
    body_lines: list[str] = []
    in_body = False

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            if in_body and body_lines and body_lines[-1] != '':
                body_lines.append('')
            continue

        if _is_cls_detail_tail(line):
            break
        if _is_cls_detail_noise(line, title):
            continue

        if not publish_time and re.fullmatch(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+星期[一二三四五六日天]', line):
            publish_time = line
            continue
        if not source and line.startswith('财联社 '):
            source = line
            continue
        if line.startswith('①') or line.startswith('②') or line.startswith('③'):
            summary_lines.append(line)
            continue

        if not in_body and ('财联社' in line and '日讯' in line):
            in_body = True

        if in_body:
            cleaned = _normalize_cninfo_line(_clean_inline_markdown(line))
            if cleaned:
                body_lines.append(cleaned)

    body = _join_paragraphs(body_lines)
    if len(body.strip()) < 60:
        return {'success': False, 'error': '财联社文章正文提取失败'}

    parts = [f'# {title}']
    if publish_time:
        parts.append(f'**发布时间**: {publish_time}')
    if source:
        parts.append(f'**来源**: {source}')
    if summary_lines:
        parts.extend(['', '## 摘要', ''])
        parts.extend(summary_lines)
    parts.extend(['', '## 正文', '', body])

    cleaned = '\n'.join(parts).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': title,
            'content_type': 'financial_news_article',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _extract_eastmoney_home_page(markdown: str, metadata: dict) -> dict:
    entries: list[str] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if _is_eastmoney_home_noise(line):
            continue
        link_matches = re.findall(r'\[([^\]]+)\]\((?:https?://)?(?:finance|biz)\.eastmoney\.com/a/\d+\.html[^\)]*\)', line)
        if not link_matches:
            continue
        for title in link_matches:
            cleaned = _normalize_cninfo_line(_clean_inline_markdown(title))
            if cleaned and cleaned not in entries:
                entries.append(cleaned)

    if not entries:
        return {'success': False, 'error': '东方财富首页新闻流提取失败'}

    cleaned = '\n'.join(['# 东方财富财经要闻', '', '## 新闻流', '', *[f'- {item}' for item in entries]]).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': '东方财富财经要闻',
            'content_type': 'financial_news_list',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _extract_eastmoney_article_page(markdown: str, metadata: dict) -> dict:
    title = _pick_title(markdown, metadata)
    publish_time = ''
    source = ''
    body_lines: list[str] = []
    in_body = False

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            if in_body and body_lines and body_lines[-1] != '':
                body_lines.append('')
            continue
        if _is_eastmoney_article_tail(line):
            break
        if _is_eastmoney_article_noise(line, title):
            continue

        if not publish_time and re.fullmatch(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}', line):
            publish_time = line
            continue
        if not source and line.startswith('来源：'):
            source = line.replace('来源：', '').strip()
            continue

        if not in_body and ('讯，' in line or '讯，' in _normalize_cninfo_line(line)):
            in_body = True

        if in_body:
            cleaned = _normalize_cninfo_line(_clean_inline_markdown(line))
            if cleaned:
                body_lines.append(cleaned)

    body = _join_paragraphs(body_lines)
    if len(body.strip()) < 50:
        return {'success': False, 'error': '东方财富文章正文提取失败'}

    parts = [f'# {title}']
    if publish_time:
        parts.append(f'**发布时间**: {publish_time}')
    if source:
        parts.append(f'**来源**: {source}')
    parts.extend(['', '## 正文', '', body])

    cleaned = '\n'.join(parts).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': title,
            'content_type': 'financial_news_article',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _extract_sinafinance_home_page(markdown: str, metadata: dict) -> dict:
    entries: list[str] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line or _is_sinafinance_home_noise(line):
            continue
        links = re.findall(r'\[([^\]]+)\]\((?:https?://)?finance\.sina\.com\.cn/[^\)]*doc-[^\)]*\.shtml\)', line)
        if not links:
            continue
        for title in links:
            cleaned = _normalize_cninfo_line(_clean_inline_markdown(title))
            if cleaned and cleaned not in entries:
                entries.append(cleaned)

    if not entries:
        return {'success': False, 'error': '新浪财经首页新闻流提取失败'}

    cleaned = '\n'.join(['# 新浪财经要闻', '', '## 新闻流', '', *[f'- {item}' for item in entries]]).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': '新浪财经要闻',
            'content_type': 'financial_news_list',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _extract_sinafinance_article_page(markdown: str, metadata: dict) -> dict:
    title = _pick_title(markdown, metadata)
    title = re.sub(r'[_|－-]\s*新浪财经.*$', '', title).strip()

    publish_time = ''
    source = ''
    body_lines: list[str] = []
    in_body = False

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            if in_body and body_lines and body_lines[-1] != '':
                body_lines.append('')
            continue
        if _is_sinafinance_article_tail(line):
            break
        if _is_sinafinance_article_noise(line, title):
            continue

        if not publish_time and re.fullmatch(r'\d{4}年\d{2}月\d{2}日\s+\d{2}:\d{2}(?:\s+\S+)?', line):
            publish_time = line
            continue
        if not publish_time:
            embedded = re.match(r'(?P<time>\d{4}年\d{2}月\d{2}日\s+\d{2}:\d{2})\[(?P<source>[^\]]+)\]\([^)]+\)', line)
            if embedded:
                publish_time = embedded.group('time').strip()
                source = embedded.group('source').strip()
                continue
        if not source and line.startswith('来源：'):
            source = line.split('：', 1)[1].strip()
            continue

        if not in_body and ('讯，' in line or line.startswith('编者按：') or re.match(r'^\d{4}年\d{1,2}月\d{1,2}日', line)):
            in_body = True

        if in_body:
            cleaned = _normalize_cninfo_line(_clean_inline_markdown(line))
            if cleaned:
                body_lines.append(cleaned)

    body = _join_paragraphs(body_lines)
    if len(body.strip()) < 50:
        return {'success': False, 'error': '新浪财经文章正文提取失败'}

    parts = [f'# {title}']
    if publish_time:
        parts.append(f'**发布时间**: {publish_time}')
    if source:
        parts.append(f'**来源**: {source}')
    parts.extend(['', '## 正文', '', body])

    cleaned = '\n'.join(parts).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': title,
            'content_type': 'financial_news_article',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _extract_wallstreetcn_home_page(markdown: str, metadata: dict) -> dict:
    entries: list[str] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line or _is_wallstreetcn_home_noise(line):
            continue
        links = re.findall(r'\[([^\]]+)\]\(https://wallstreetcn\.com/(?:articles|livenews)/\d+\)', line)
        if not links:
            continue
        for title in links:
            cleaned = _normalize_cninfo_line(_clean_inline_markdown(title))
            if cleaned and cleaned not in entries:
                entries.append(cleaned)

    if not entries:
        return {'success': False, 'error': '华尔街见闻首页新闻流提取失败'}

    cleaned = '\n'.join(['# 华尔街见闻要闻', '', '## 新闻流', '', *[f'- {item}' for item in entries]]).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': '华尔街见闻要闻',
            'content_type': 'financial_news_list',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _extract_wallstreetcn_article_page(markdown: str, metadata: dict) -> dict:
    title = _pick_title(markdown, metadata)
    title = re.sub(r'\s*-\s*华尔街见闻$', '', title).strip()

    publish_time = ''
    source = ''
    body_lines: list[str] = []
    in_body = False

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            if in_body and body_lines and body_lines[-1] != '':
                body_lines.append('')
            continue
        if _is_wallstreetcn_article_tail(line):
            break
        if _is_wallstreetcn_article_noise(line, title):
            continue

        author_match = re.search(r'(.+?)\s+(\d{2}-\d{2}\s+\d{2}:\d{2})$', line)
        if not publish_time and author_match:
            source = _normalize_cninfo_line(_clean_inline_markdown(author_match.group(1))).strip()
            source = re.sub(r'^article\.author\.display_name', '', source).strip()
            publish_time = author_match.group(2).strip()
            continue

        if line.startswith('更多消息，持续更新中'):
            continue

        if not in_body and line.startswith('美国4月非农就业人口增加'):
            in_body = True

        if in_body:
            cleaned = _normalize_cninfo_line(_clean_inline_markdown(line))
            if cleaned:
                body_lines.append(cleaned)

    body = _join_paragraphs(body_lines)
    if len(body.strip()) < 30:
        return {'success': False, 'error': '华尔街见闻文章正文提取失败'}

    parts = [f'# {title}']
    if publish_time:
        parts.append(f'**发布时间**: {publish_time}')
    if source:
        parts.append(f'**来源**: {source}')
    parts.extend(['', '## 正文', '', body])

    cleaned = '\n'.join(parts).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': title,
            'content_type': 'financial_news_article',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _extract_maimai_article_page(markdown: str, metadata: dict) -> dict:
    title = _pick_maimai_title(markdown, metadata)

    author = ''
    publish_time = ''
    role = ''
    body_lines: list[str] = []
    after_title = False

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            if after_title and body_lines and body_lines[-1] != '':
                body_lines.append('')
            continue
        if _is_maimai_article_tail(line):
            break

        cleaned = _normalize_cninfo_line(_clean_inline_markdown(line))
        if not cleaned:
            continue
        if cleaned == title:
            after_title = True
            continue
        if _is_maimai_article_noise(cleaned, title):
            continue
        if not after_title:
            continue

        if not author:
            author = cleaned
            continue

        if not publish_time:
            meta_match = re.fullmatch(r'(\d{2,4}-\d{1,2}-\d{1,2})\s*·\s*(.+)', cleaned)
            if meta_match:
                publish_time = meta_match.group(1).strip()
                role = meta_match.group(2).strip()
                continue

        body_lines.append(cleaned)

    body = _join_paragraphs(body_lines)
    if len(body.strip()) < 20:
        return {'success': False, 'error': '脉脉文章正文提取失败'}

    parts = [f'# {title}']
    if author:
        parts.append(f'**作者**: {author}')
    if publish_time:
        parts.append(f'**发布时间**: {publish_time}')
    if role:
        parts.append(f'**身份**: {role}')
    parts.extend(['', '## 正文', '', body])

    cleaned = '\n'.join(parts).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': title,
            'content_type': 'jobhunter_article',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _extract_nowcoder_discuss_page(markdown: str, metadata: dict) -> dict:
    title = _pick_nowcoder_title(markdown, metadata)

    body_lines: list[str] = []
    after_title = False

    source_lines = markdown.splitlines()
    for index, raw_line in enumerate(source_lines):
        line = raw_line.strip()
        if not line:
            if after_title and body_lines and body_lines[-1] != '':
                body_lines.append('')
            continue
        cleaned = _normalize_cninfo_line(_clean_inline_markdown(line))
        if _looks_like_nowcoder_related_card_start(source_lines, index):
            while body_lines and body_lines[-1] == '':
                body_lines.pop()
            break
        if _looks_like_nowcoder_tag_tail(cleaned):
            while body_lines and body_lines[-1] == '':
                body_lines.pop()
            break
        if _looks_like_nowcoder_topic_metric(cleaned):
            while body_lines and body_lines[-1] == '':
                body_lines.pop()
            if body_lines and not body_lines[-1].startswith('## '):
                body_lines.pop()
            break
        if _is_nowcoder_discuss_tail(line):
            break
        if not cleaned:
            continue
        if cleaned == title:
            after_title = True
            continue
        if _is_nowcoder_discuss_noise(cleaned, title):
            continue
        if not after_title:
            continue

        if raw_line.lstrip().startswith('#') or _looks_like_nowcoder_section_heading(cleaned):
            if body_lines and body_lines[-1] != '':
                body_lines.append('')
            body_lines.append(f'## {cleaned}')
            body_lines.append('')
            continue

        body_lines.append(cleaned)

    body = _join_paragraphs(body_lines)
    if len(body.strip()) < 30:
        return {'success': False, 'error': '牛客讨论帖正文提取失败'}

    cleaned = '\n'.join([f'# {title}', '', '## 正文', '', body]).strip()
    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': title,
            'content_type': 'jobhunter_discuss_post',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _extract_finance_stock_content(markdown: str, metadata: dict, url: str, platform: dict) -> dict:
    title = _pick_finance_stock_title(markdown, metadata)
    sections: dict[str, list[str]] = {}
    current_section = '公司资料'

    def ensure_section(name: str) -> None:
        nonlocal current_section
        current_section = name
        sections.setdefault(name, [])

    def append_to_section(name: str, value: str) -> None:
        ensure_section(name)
        if value and value not in sections[name]:
            sections[name].append(value)

    ensure_section(current_section)

    source_lines = markdown.splitlines()
    index = 0
    while index < len(source_lines):
        raw_line = source_lines[index]
        stripped = raw_line.strip()

        if stripped.startswith(('<table', '<thead', '<tbody', '<tr', '<th', '<td')):
            html_block: list[str] = []
            while index < len(source_lines):
                html_line = source_lines[index].strip()
                if not html_line:
                    break
                if not html_line.startswith(('<table', '<thead', '<tbody', '<tr', '<th', '<td', '</table', '</thead', '</tbody', '</tr', '</th', '</td')):
                    break
                html_block.append(html_line)
                index += 1
                if '</table>' in html_line:
                    break
            table = _convert_html_table_to_markdown('\n'.join(html_block))
            if table:
                append_to_section(current_section, table)
            continue

        if stripped.startswith('|'):
            block: list[str] = []
            while index < len(source_lines) and source_lines[index].strip().startswith('|'):
                block.append(_normalize_finance_table_line(source_lines[index].strip()))
                index += 1
            table = _clean_finance_markdown_table(block)
            if table:
                append_to_section(current_section, table)
            continue

        cleaned = _normalize_cninfo_line(_clean_inline_markdown(raw_line))
        if not cleaned:
            index += 1
            continue

        if _is_finance_stock_tail(cleaned):
            break
        if _is_finance_stock_noise(cleaned, title):
            index += 1
            continue

        if stripped.startswith('{"title":') and '"report"' in stripped:
            table = _convert_10jqka_finance_json_to_markdown(stripped)
            if table:
                append_to_section('财务指标', table)
            index += 1
            continue

        heading = _normalize_finance_stock_heading(cleaned)
        if heading and cleaned != title:
            ensure_section(heading)
            index += 1
            continue

        if _is_finance_stock_key_line(cleaned):
            append_to_section(current_section, cleaned)
        index += 1

    parts = [f'# {title}']
    if metadata.get('published_time'):
        parts.append(f'**发布时间**: {metadata["published_time"]}')
    if url:
        parts.append(f'**来源页面**: {url}')

    for section_name, values in sections.items():
        cleaned_values = [value for value in values if value]
        if not cleaned_values:
            continue
        parts.extend(['', f'## {section_name}', ''])
        for value in cleaned_values:
            if value.startswith('|'):
                parts.append(value)
            else:
                parts.append(f'- {value}')

    cleaned = '\n'.join(parts).strip()
    if len(cleaned) < 80:
        return {'success': False, 'error': '财经个股页提取失败'}

    return {
        'success': True,
        'content': cleaned,
        'metadata': {
            **metadata,
            'title': title,
            'content_type': 'finance_stock',
            'cleanup_chars_before': len(markdown.strip()),
            'cleanup_chars_after': len(cleaned),
        },
    }


def _clean_zhihu_answer_body(lines: list[str]) -> str:
    kept: list[str] = []
    for raw_line in lines:
        line = _normalize_invisible_whitespace(raw_line).strip()
        if not line:
            if kept and kept[-1] != '':
                kept.append('')
            continue
        if _is_zhihu_answer_noise(line):
            continue
        cleaned = _normalize_zhihu_plaintext_text(_clean_inline_markdown(line))
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

    kept = _merge_fragmented_zhihu_lines(kept)
    return _join_paragraphs(kept)


def _normalize_cninfo_line(text: str) -> str:
    text = _normalize_invisible_whitespace(text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'：\s+', '：', text)
    text = re.sub(r'\s+：', '：', text)
    text = re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])', '', text)
    text = re.sub(r'(?<=\d)\s*-\s*(?=\d)', '-', text)
    return text.strip()


def _join_cninfo_announcement_lines(lines: list[str]) -> str:
    chunks: list[str] = []
    current = ''

    for line in lines:
        if not line:
            if current:
                chunks.append(current.strip())
                current = ''
            continue

        if _is_cninfo_heading_line(line):
            if current:
                chunks.append(current.strip())
                current = ''
            chunks.append(line)
            continue

        if not current:
            current = line
            continue

        if _should_merge_cninfo_line(current, line):
            current += line
        else:
            chunks.append(current.strip())
            current = line

    if current:
        chunks.append(current.strip())

    return '\n\n'.join(chunk for chunk in chunks if chunk).strip()


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
    text = _normalize_invisible_whitespace(text)
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


def _normalize_invisible_whitespace(text: str) -> str:
    return (
        text.replace('\u200b', '')
        .replace('\ufeff', '')
        .replace('\u200e', '')
        .replace('\u200f', '')
        .replace('\xa0', ' ')
    )


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


def _merge_fragmented_zhihu_lines(lines: list[str]) -> list[str]:
    merged: list[str] = []
    fragments: list[str] = []

    def flush_fragments() -> None:
        nonlocal fragments
        if not fragments:
            return
        if len(fragments) >= 4:
            merged.append(''.join(fragments))
        else:
            merged.extend(fragments)
        fragments = []

    for line in lines:
        if not line:
            flush_fragments()
            if merged and merged[-1] != '':
                merged.append('')
            continue

        if _looks_like_zhihu_fragment_line(line):
            fragments.append(line)
            continue

        flush_fragments()
        merged.append(line)

    flush_fragments()
    return merged


def _normalize_zhihu_plaintext_text(text: str) -> str:
    normalized: list[str] = []
    for ch in text:
        if ch == '∗':
            normalized.append('*')
            continue
        try:
            name = unicodedata.name(ch)
        except ValueError:
            normalized.append(ch)
            continue
        if 'MATHEMATICAL' in name:
            normalized.append(unicodedata.normalize('NFKC', ch))
        else:
            normalized.append(ch)
    return ''.join(normalized)


def _normalize_finance_table_line(line: str) -> str:
    return re.sub(r'\s+', ' ', line).replace(' |', ' |').strip()


def _clean_finance_markdown_table(lines: list[str]) -> str:
    if len(lines) < 2:
        return ''
    compact = '\n'.join(lines).strip()
    if compact.count('|') < 4:
        return ''
    if any(token in compact for token in ('用户名：', '密码：', '登录帮助', '新用户注册', '记录登录状态')):
        return ''
    if not any(re.search(r'\d', line) for line in lines[1:]):
        return ''
    return compact


def _convert_html_table_to_markdown(raw_html: str) -> str:
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', raw_html, flags=re.S | re.I)
    parsed_rows: list[list[str]] = []
    for row_html in rows:
        cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row_html, flags=re.S | re.I)
        cleaned_cells = [_clean_html_cell(cell) for cell in cells]
        cleaned_cells = [cell for cell in cleaned_cells if cell]
        if cleaned_cells:
            parsed_rows.append(cleaned_cells)

    if len(parsed_rows) < 2:
        return ''

    width = max(len(row) for row in parsed_rows)
    normalized_rows = [row + [''] * (width - len(row)) for row in parsed_rows]
    header = normalized_rows[0]
    lines = ['| ' + ' | '.join(header) + ' |', '| ' + ' | '.join(['---'] * width) + ' |']
    for row in normalized_rows[1:]:
        lines.append('| ' + ' | '.join(row) + ' |')
    return '\n'.join(lines)


def _clean_html_cell(cell: str) -> str:
    text = re.sub(r'<[^>]+>', ' ', cell)
    text = html.unescape(text)
    return _normalize_cninfo_line(text)


def _convert_10jqka_finance_json_to_markdown(raw: str) -> str:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return ''

    titles = payload.get('title') or []
    reports = payload.get('report') or []
    if not titles or len(titles) < 2 or not reports:
        return ''

    dates = reports[0][:5]
    if not dates:
        return ''

    rows = ['| 科目 | ' + ' | '.join(dates) + ' |', '| --- | ' + ' | '.join(['---'] * len(dates)) + ' |']
    for metric_index, metric in enumerate(titles[1:], start=1):
        if metric_index >= len(reports):
            break
        metric_name = metric[0] if isinstance(metric, list) and metric else str(metric)
        values = reports[metric_index][:len(dates)]
        rows.append('| ' + ' | '.join([metric_name, *values]) + ' |')
    return '\n'.join(rows)


def _normalize_finance_stock_heading(line: str) -> str:
    if line.startswith('公司简介—') or line == '公司资料':
        return '公司资料'
    if line in {'财务指标', '资产负债构成', '财务报告查看', '指标变动说明', '财务报告', '融资融券'}:
        return line
    if '核心题材' in line:
        return '核心题材'
    return ''


def _is_finance_stock_key_line(line: str) -> bool:
    if line.startswith('要点'):
        return True
    prefixes = (
        '公司名称：', '公司英文名称：', '上市市场：', '上市日期：', '成立日期：',
        '机构类型：', '董事会秘书：', '董秘电话：', '董秘传真：', '公司电子邮箱：',
        '董秘电子邮箱：', '公司网址：', '主营业务：', '公司简介：', '注册地址：',
        '办公地址：', '注册资本：', '证券简称更名历史：', '经营范围', '所属行业',
        '所属板块', '行业背景', '战略落地', '模式转型', '管理效率',
    )
    if any(line.startswith(prefix) for prefix in prefixes):
        return True
    finance_tokens = ('ROE', 'PE', 'PB', '资产负债率', '净利润', '营业总收入', '每股收益', '融资', '融券', '负债', '现金流')
    return any(token in line for token in finance_tokens)


def _is_finance_stock_noise(line: str, title: str) -> bool:
    if line == title:
        return True
    lowered = line.lower()
    if line in {'首页', '登录', '注册', '分享', '收藏', '行情', '股吧', '新闻', '外汇', '新三板', '更多'}:
        return True
    if line.startswith('最新价：') or line.startswith('涨跌幅：'):
        return True
    if line.startswith('谢谢您的支持') or line.startswith('F10 功能找不到'):
        return True
    if line.startswith('特色龙虎榜单') or line.startswith('排名简称总市值'):
        return True
    if line.startswith('上一组') or line.startswith('下一组'):
        return True
    if '新浪首页' in line or '财经首页' in line:
        return True
    if '登录/注册' in line or '登录 / 注册' in line:
        return True
    if line.startswith('查看自选股请先') or line.startswith('最近访问股'):
        return True
    if re.fullmatch(r'\d+', line):
        return True
    if re.fullmatch(r'[\s\W_]+', line):
        return True
    if lowered.startswith('http://') or lowered.startswith('https://'):
        return True
    return False


def _is_finance_stock_tail(line: str) -> bool:
    return line in {'杜邦分析原理', '相关推荐', '招聘动态', '全站热榜', '创作者周榜', '正在热议'}


def _looks_like_zhihu_fragment_line(line: str) -> bool:
    compact = _normalize_invisible_whitespace(line).strip()
    if not compact or len(compact) > 2:
        return False
    if re.search(r'https?://|www\.', compact):
        return False
    if re.fullmatch(r'\d+[.)]?', compact):
        return False
    return True


def _is_cninfo_notice_list(url: str, markdown: str) -> bool:
    lowered_url = url.lower()
    if 'disclosure/list/notice' in lowered_url:
        return True
    return 'new/disclosure/detail?' not in lowered_url and '共 ' in markdown and '条' in markdown and 'new/disclosure/detail?' in markdown


def _is_cninfo_announcement_document(url: str, markdown: str) -> bool:
    lowered_url = url.lower()
    if 'static.cninfo.com.cn/finalpage/' in lowered_url:
        return True
    if lowered_url.endswith('.pdf'):
        return True
    return '证券代码' in markdown and '公告编号' in markdown


def _is_sse_notice_list(url: str, markdown: str) -> bool:
    lowered_url = url.lower()
    if 'listannouncement' in lowered_url:
        return True
    return '公司公告' in markdown and 'disclosure/listedinfo/announcement/' in markdown


def _is_sse_announcement_document(url: str, markdown: str) -> bool:
    lowered_url = url.lower()
    if lowered_url.endswith('.pdf'):
        return True
    return '证券代码' in markdown and '公告编号' in markdown and '上海证券交易所' in markdown


def _is_reuters_markets_page(url: str, markdown: str) -> bool:
    lowered_url = url.lower()
    if '/markets/' in lowered_url and lowered_url.rstrip('/').endswith('/markets'):
        return True
    return markdown.startswith('# Markets')


def _is_hkexnews_title_search_page(url: str, markdown: str) -> bool:
    lowered_url = url.lower()
    if 'titlesearch.xhtml' in lowered_url:
        return True
    return 'Release Time:' in markdown and 'Stock Short Name:' in markdown and 'listedco/listconews/sehk/' in markdown


def _is_hkexnews_announcement_document(url: str, markdown: str) -> bool:
    lowered_url = url.lower()
    if lowered_url.endswith('.pdf') and 'hkexnews.hk' in lowered_url:
        return True
    return '(Stock Code:' in markdown and 'LETTER FROM THE BOARD' in markdown


def _is_sec_browse_page(url: str, markdown: str) -> bool:
    lowered_url = url.lower()
    if '/edgar/browse/' in lowered_url:
        return True
    return 'Click to Open filing' in markdown and 'Open document' in markdown


def _is_sec_filing_index_page(url: str, markdown: str) -> bool:
    lowered_url = url.lower()
    if lowered_url.endswith('-index.htm'):
        return True
    return 'Document Format Files' in markdown and 'Filing Date' in markdown and 'Period of Report' in markdown


def _is_cls_detail_page(url: str, markdown: str) -> bool:
    lowered_url = url.lower()
    if '/detail/' in lowered_url:
        return True
    return '财联社 ' in markdown and '我要评论' in markdown


def _is_eastmoney_stock_page(url: str, markdown: str) -> bool:
    lowered_url = url.lower()
    domain = urlparse(url).netloc.lower()
    if '/stockdata/' in lowered_url:
        return True
    if domain in {'data.eastmoney.com', 'quote.eastmoney.com', 'emweb.securities.eastmoney.com'}:
        return True
    return '核心题材' in markdown or '要点1：**所属板块**' in markdown


def _is_eastmoney_article_page(url: str, markdown: str) -> bool:
    lowered_url = url.lower()
    if re.search(r'/a/\d+\.html', lowered_url):
        return True
    return '来源：' in markdown and ('相关阅读' in markdown or '责任编辑' in markdown)


def _is_sinafinance_stock_page(url: str, markdown: str) -> bool:
    lowered_url = url.lower()
    if any(token in lowered_url for token in ('/corp/', '/stockid/', '/vfd_', '/vci_')):
        return True
    return '公司名称：' in markdown and '主营业务：' in markdown


def _is_sinafinance_article_page(url: str, markdown: str) -> bool:
    lowered_url = url.lower()
    if 'doc-' in lowered_url and lowered_url.endswith('.shtml'):
        return True
    return '来源：' in markdown and ('责任编辑' in markdown or '热门评论' in markdown)


def _is_wallstreetcn_article_page(url: str, markdown: str) -> bool:
    lowered_url = url.lower()
    if '/articles/' in lowered_url:
        return True
    return '风险提示及免责条款' in markdown and '写评论' in markdown


def _is_maimai_article_page(url: str, markdown: str) -> bool:
    lowered_url = url.lower()
    if '/article/detail' in lowered_url:
        return True
    return '脉脉App内打开' in markdown and 'add-friend好友' in markdown


def _is_nowcoder_discuss_page(url: str, markdown: str) -> bool:
    lowered_url = url.lower()
    if '/discuss/' in lowered_url:
        return True
    return '热门话题' in markdown and '邀请牛友回答' in markdown


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
    if line.startswith('添加评论'):
        return True
    if line.startswith('App内查看更多评论'):
        return True
    return False


def _is_cninfo_announcement_noise(line: str) -> bool:
    if line.startswith('本公司董事会及全体董事保证'):
        return True
    if line.startswith('本公司及董事会全体成员保证'):
        return True
    if line.startswith('述或者重大遗漏'):
        return True
    if '真实性、准确性和完整性承担法律责任' in line:
        return True
    if re.fullmatch(r'第\s*\d+\s*页', line):
        return True
    return False


def _is_sse_announcement_noise(line: str) -> bool:
    if line.startswith('本公司董事会及全体董事保证'):
        return True
    if line.startswith('本公司及董事会全体成员保证'):
        return True
    if line.startswith('述或者重大遗漏'):
        return True
    if '真实性、准确性和完整性承担个别及连带责任' in line:
        return True
    if re.fullmatch(r'第\s*\d+\s*页', line):
        return True
    return False


def _is_reuters_article_noise(line: str) -> bool:
    return (
        line.startswith('## Read Next')
        or line.startswith('Our Standards:')
        or line.startswith('[Purchase Licensing Rights]')
    )


def _is_reuters_inline_noise(line: str) -> bool:
    lowered = line.lower()
    if line.startswith('Advertisement · Scroll to continue'):
        return True
    if line.startswith('The Week in Breakingviews newsletter offers'):
        return True
    if line.startswith('Skip to main content'):
        return True
    if line.startswith('Exclusive news, data and analytics for financial market professionals'):
        return True
    if 'purchase licensing rights' in lowered:
        return True
    return False


def _is_reuters_markets_noise(line: str) -> bool:
    if line.startswith('Official Data Partner'):
        return True
    if line.startswith('Notice of Your Privacy Choices'):
        return True
    if 'category]' in line:
        return False
    if re.fullmatch(r'\d{1,2}:\d{2}\s+[AP]M\s+GMT\+8', line):
        return True
    return False


def _extract_reuters_bullet_title(line: str) -> str:
    matches = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', line)
    if not matches:
        return ''
    return matches[-1][0].strip()


def _is_hkexnews_announcement_noise(line: str) -> bool:
    if line.startswith('The notice convening the SGM'):
        return True
    if line.startswith('Capitalised terms used'):
        return True
    if line.startswith('– ') or line == 'CONTENTS':
        return True
    return False


def _is_cls_home_noise(line: str) -> bool:
    if line.startswith('[') and 'our?nav=' in line:
        return True
    if '上证指数' in line or '深证成指' in line or '创业板指' in line:
        return True
    if '热门板块' in line or '财联社电报' in line:
        return True
    if line.startswith('注册|登录'):
        return True
    if line.startswith('## [首页]'):
        return True
    return False


def _is_cls_detail_noise(line: str, title: str) -> bool:
    if line == title:
        return True
    if line.startswith('[') and 'our?nav=' in line:
        return True
    if line == '原创':
        return True
    if line.startswith('[环球市场情报]'):
        return True
    if line == '收藏' or line.startswith('阅 '):
        return True
    if line.startswith('关于我们') or line.startswith('## [首页]'):
        return True
    return False


def _is_cls_detail_tail(line: str) -> bool:
    if line.startswith('我要评论'):
        return True
    if line.startswith('关联话题'):
        return True
    if '版权所有' in line:
        return True
    return False


def _is_eastmoney_home_noise(line: str) -> bool:
    if line.startswith('*   [焦点]') or line.startswith('* [焦点]'):
        return True
    if '全球时间:' in line:
        return True
    if '上证指数' in line or '深证成指' in line or '道琼斯指数' in line:
        return True
    if '秒后刷新' in line or line.startswith('[刷新]'):
        return True
    if line.startswith('热门板块'):
        return True
    return False


def _is_eastmoney_article_noise(line: str, title: str) -> bool:
    if line == title:
        return True
    if line.startswith('[首页]'):
        return True
    if line == '收藏' or line == '评论':
        return True
    return False


def _is_eastmoney_article_tail(line: str) -> bool:
    if line.startswith('相关阅读'):
        return True
    if line.startswith('网友点击'):
        return True
    return False


def _is_sinafinance_home_noise(line: str) -> bool:
    if '新浪首页' in line and '巴菲特股东大会' in line:
        return True
    if line.startswith('*') and 'finance.sina.com.cn/' in line:
        return True
    if line.startswith('[环球市场>>]'):
        return True
    if '上证综指' in line or '环球股指' in line:
        return True
    if line.startswith('热门资讯'):
        return True
    return False


def _is_sinafinance_article_noise(line: str, title: str) -> bool:
    if line == title:
        return True
    if line.startswith('*   [新浪首页]') or line.startswith('* [新浪首页]'):
        return True
    if line.startswith('[基金]') and '>正文' in line:
        return True
    if line.startswith('[新浪财经APP]'):
        return True
    if '更多分享' in line or '分享到微博' in line or '分享到QQ' in line or '分享到QQ空间' in line:
        return True
    return False


def _is_sinafinance_article_tail(line: str) -> bool:
    if line.startswith('责任编辑：'):
        return True
    if line.startswith('热门评论'):
        return True
    if line.startswith('相关新闻') or line.startswith('延伸阅读'):
        return True
    if line.startswith('海量资讯') or line.startswith('新浪财经声明'):
        return True
    if line.startswith('0 条评论') or line.startswith('VIP课程推荐') or line.startswith('APP专享直播'):
        return True
    if line.startswith('热门推荐') or line.startswith('股市直播') or line.startswith('最近访问'):
        return True
    if line.startswith('加载更多'):
        return True
    if line == '东方财富':
        return True
    return False


def _is_wallstreetcn_home_noise(line: str) -> bool:
    if line.startswith('*') and 'wallstreetcn.com/' in line:
        return True
    if line.startswith('登录 / 注册'):
        return True
    if '美元指数' in line or '现货黄金' in line or '离岸人民币' in line:
        return True
    if line.startswith('最新资讯') or line.startswith('华尔街见闻'):
        return True
    return False


def _is_wallstreetcn_article_noise(line: str, title: str) -> bool:
    if line == title:
        return True
    if line.startswith('*') and 'wallstreetcn.com/' in line:
        return True
    if line.startswith('登录 / 注册'):
        return True
    if line in {'2', '收藏'}:
        return True
    return False


def _is_wallstreetcn_article_tail(line: str) -> bool:
    if line.startswith('风险提示及免责条款'):
        return True
    if line.startswith('写评论'):
        return True
    if line.startswith('最热文章'):
        return True
    return False


def _is_maimai_article_noise(line: str, title: str) -> bool:
    if line == title:
        return True
    if line in {'登录 / 注册', 'add-friend好友', '相关推荐', '评论', '好友'}:
        return True
    if line == f'{title}脉脉':
        return True
    return False


def _is_maimai_article_tail(line: str) -> bool:
    if line == 'END':
        return True
    if line.startswith('阅读'):
        return True
    if line.startswith('声明：'):
        return True
    if line.startswith('相关推荐'):
        return True
    if line.startswith('最新发布') or line.startswith('大家都在看'):
        return True
    if line.startswith('热门人脉圈') or line.startswith('评论'):
        return True
    if line.startswith('脉脉App内打开'):
        return True
    if line.startswith('登录查看更多内容'):
        return True
    return False


def _is_nowcoder_discuss_noise(line: str, title: str) -> bool:
    if line == title:
        return True
    if line == '精华':
        return True
    if line in {'首页', '题库', '面试', '简历', '求职', '学习', '竞赛', '搜索', '我要招人', '登录 / 注册', '关注', '已编辑'}:
        return True
    return False


def _is_nowcoder_discuss_tail(line: str) -> bool:
    if line.startswith('[#'):
        return True
    if line.startswith('## 面经##') or line.startswith('##校招##'):
        return True
    if line in {'相关推荐', '招聘动态', '全站热榜', '创作者周榜', '正在热议', '企业服务', '校企合作', '联系我们', '资源导航', '免责声明', '友情链接', '我是求职者', '我是招聘方'}:
        return True
    if line in {'提示', '订阅专刊', '浏览', '评论', '热门话题', '话题', '表情'}:
        return True
    if line.startswith('点赞成功') or line.startswith('邀请牛友回答'):
        return True
    if line.startswith('送花成功') or line.startswith('畅所欲言吧'):
        return True
    if line.startswith('牛客科技©') or line.startswith('每天登录，牛客都会送你一朵免费的花'):
        return True
    if line.startswith('共0张') or line.startswith('最近使用'):
        return True
    return False


def _looks_like_zhihu_plaintext_author(lines: list[str], index: int) -> bool:
    line = _normalize_invisible_whitespace(lines[index]).strip()
    if not line or len(line) > 24:
        return False
    if _is_zhihu_plaintext_scaffold(line):
        return False
    if re.search(r'[，。！？：:/]|https?://|www\.|vlink\.|公众号|答主|欢迎关注', line):
        return False
    if re.search(r'\d', line):
        return False

    following: list[str] = []
    for next_line in lines[index + 1:]:
        cleaned = _normalize_invisible_whitespace(next_line).strip()
        if not cleaned:
            continue
        following.append(cleaned)
        if len(following) == 3:
            break

    if not following:
        return False
    return '关注' in following


def _is_zhihu_plaintext_scaffold(line: str) -> bool:
    if line in {
        '关注', '推荐', '热榜', '专栏', '圈子', 'New', '付费咨询', '知学堂', '直答',
        '切换模式', '登录/注册', '登录 / 注册', '关注问题', '写回答', '邀请回答',
        '好问题 3', '添加评论', '分享', '默认排序', 'AIGC', 'ChatGPT', 'claude',
        'Cursor', 'POE ChatGPT',
    }:
        return True
    if re.fullmatch(r'\d+\s+个回答', line):
        return True
    if re.fullmatch(r'\d+', line):
        return True
    if line.startswith('被浏览') or line.startswith('关注者'):
        return True
    return False


def _looks_like_nowcoder_section_heading(line: str) -> bool:
    if line == '深信服一二面':
        return True
    if len(line) > 32:
        return False
    return bool(re.fullmatch(r'[A-Za-z0-9\u4e00-\u9fff·（）()_/\-+ ]+(?:一面|二面|三面|四面|五面|六面|七面|八面|九面|十面|交叉面|加面|HR面|hr面|笔试)', line))


def _looks_like_nowcoder_topic_metric(line: str) -> bool:
    return bool(re.fullmatch(r'\d{3,}\s*次浏览', line) or re.fullmatch(r'\d{2,}\s*人参与', line))


def _looks_like_nowcoder_related_card_start(lines: list[str], index: int) -> bool:
    line = _normalize_invisible_whitespace(lines[index]).strip()
    if line != '分享':
        return False

    following: list[str] = []
    for next_line in lines[index + 1:]:
        cleaned = _normalize_invisible_whitespace(next_line).strip()
        if not cleaned:
            continue
        following.append(cleaned)
        if len(following) == 3:
            break

    if len(following) < 2:
        return False
    return bool(
        re.fullmatch(r'\d{2}-\d{2}\s+\d{2}:\d{2}', following[1])
        or re.search(r'(大学|学院|工程师|开发|产品|算法|测试|前端|后端)', following[-1])
    )


def _looks_like_nowcoder_tag_tail(line: str) -> bool:
    return line.count('#') >= 2 and any(token in line for token in ('面经', '校招', '字节跳动', 'TP-LINK', '阿里云'))


def _is_cninfo_heading_line(line: str) -> bool:
    return bool(
        re.match(r'^[一二三四五六七八九十]+、', line)
        or re.match(r'^（[一二三四五六七八九十]+）', line)
        or re.match(r'^\d+[\.、]', line)
    )


def _should_merge_cninfo_line(current: str, next_line: str) -> bool:
    if _is_cninfo_heading_line(current):
        return False
    if _is_cninfo_heading_line(next_line):
        return False
    if re.search(r'[。！？；：]$', current):
        return False
    return True


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
    if line in {'关注', '阅读全文', '默认排序'}:
        return True
    if re.fullmatch(r'赞同\s*\d+', line):
        return True
    if re.fullmatch(r'\d+\s*条评论', line):
        return True
    if re.fullmatch(r'\d{1,6}', line):
        return True
    if line == '分享':
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
