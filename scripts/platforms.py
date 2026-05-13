"""
Platform identification — single source of truth.
Each platform defines its domain patterns, preferred strategy order,
and cleanup profile for token-aware postprocessing.
"""

from urllib.parse import urlparse

# Strategy order is tried left-to-right by the orchestrator.
PLATFORMS = {
    'wechat': {
        'name': '微信公众号',
        'domains': ['mp.weixin.qq.com'],
        'preferred_strategies': ['firecrawl', 'opencli_browser', 'playwright', 'jina'],
        'cleanup_profile': 'wechat_article',
    },
    'xiaohongshu': {
        'name': '小红书',
        'domains': ['xiaohongshu.com', 'xhslink.com'],
        'preferred_strategies': ['firecrawl', 'opencli_browser', 'jina', 'playwright'],
        'cleanup_profile': 'social_note',
    },
    'toutiao': {
        'name': '今日头条',
        'domains': ['toutiao.com'],
        'preferred_strategies': ['firecrawl', 'opencli_browser', 'jina', 'playwright'],
        'cleanup_profile': 'article_feed',
    },
    'douyin': {
        'name': '抖音',
        'domains': ['douyin.com', 'v.douyin.com'],
        'preferred_strategies': ['firecrawl', 'opencli_browser', 'jina', 'playwright'],
        'cleanup_profile': 'short_video',
    },
    'taobao': {
        'name': '淘宝',
        'domains': ['taobao.com', 'item.taobao.com'],
        'preferred_strategies': ['firecrawl', 'opencli_browser', 'playwright', 'jina'],
        'cleanup_profile': 'ecommerce',
    },
    'tmall': {
        'name': '天猫',
        'domains': ['tmall.com', 'detail.tmall.com'],
        'preferred_strategies': ['firecrawl', 'opencli_browser', 'playwright', 'jina'],
        'cleanup_profile': 'ecommerce',
    },
    'jd': {
        'name': '京东',
        'domains': ['jd.com', 'item.jd.com'],
        'preferred_strategies': ['firecrawl', 'opencli_browser', 'jina', 'playwright'],
        'cleanup_profile': 'ecommerce',
    },
    'zhihu': {
        'name': '知乎',
        'domains': ['zhihu.com', 'zhuanlan.zhihu.com'],
        'preferred_strategies': ['firecrawl', 'cloakbrowser', 'opencli_browser', 'jina', 'playwright'],
        'cleanup_profile': 'article_feed',
    },
    'maimai': {
        'name': '脉脉',
        'domains': ['maimai.cn', 'www.maimai.cn'],
        'preferred_strategies': ['firecrawl', 'cloakbrowser', 'opencli_browser', 'jina', 'playwright'],
        'cleanup_profile': 'generic',
    },
    'nowcoder': {
        'name': '牛客',
        'domains': ['nowcoder.com', 'www.nowcoder.com'],
        'preferred_strategies': ['firecrawl', 'cloakbrowser', 'opencli_browser', 'jina', 'playwright'],
        'cleanup_profile': 'generic',
    },
    'weibo': {
        'name': '微博',
        'domains': ['weibo.com', 'm.weibo.cn'],
        'preferred_strategies': ['firecrawl', 'opencli_browser', 'playwright', 'jina'],
        'cleanup_profile': 'social_note',
    },
    'x': {
        'name': 'X',
        'domains': ['x.com', 'twitter.com', 'mobile.twitter.com'],
        'preferred_strategies': ['jina', 'opencli_browser', 'playwright', 'firecrawl'],
        'cleanup_profile': 'x_post',
    },
    'v2ex': {
        'name': 'V2EX',
        'domains': ['v2ex.com', 'www.v2ex.com'],
        'preferred_strategies': ['jina', 'opencli_browser', 'playwright'],
        'cleanup_profile': 'forum_thread',
    },
    'bilibili': {
        'name': 'B站',
        'domains': ['bilibili.com', 'b23.tv'],
        'preferred_strategies': ['firecrawl', 'opencli_browser', 'jina', 'playwright'],
        'cleanup_profile': 'short_video',
    },
    'baidu': {
        'name': '百度',
        'domains': ['baidu.com', 'baijiahao.baidu.com'],
        'preferred_strategies': ['firecrawl', 'opencli_browser', 'jina', 'playwright'],
        'cleanup_profile': 'article_feed',
    },
    '10jqka': {
        'name': '同花顺',
        'domains': ['10jqka.com.cn', 'basic.10jqka.com.cn', 'stockpage.10jqka.com.cn', 'stock.10jqka.com.cn', 'yuanchuang.10jqka.com.cn'],
        'preferred_strategies': ['playwright', 'opencli_browser', 'jina'],
        'cleanup_profile': 'finance_stock',
    },
    'cninfo': {
        'name': '巨潮资讯',
        'domains': ['cninfo.com.cn', 'www.cninfo.com.cn', 'static.cninfo.com.cn'],
        'preferred_strategies': ['jina', 'opencli_browser', 'playwright'],
        'cleanup_profile': 'generic',
    },
    'sse': {
        'name': '上交所',
        'domains': ['sse.com.cn', 'www.sse.com.cn', 'star.sse.com.cn', 'big5.sse.com.cn', 'static.sse.com.cn'],
        'preferred_strategies': ['jina', 'opencli_browser', 'playwright'],
        'cleanup_profile': 'generic',
    },
    'meowvps': {
        'name': 'MeowVPS',
        'domains': ['meowvps.com', 'www.meowvps.com'],
        'preferred_strategies': ['jina', 'opencli_browser', 'playwright'],
        'cleanup_profile': 'meowvps',
    },
    'hostloc': {
        'name': 'HostLoc',
        'domains': ['hostloc.com', 'www.hostloc.com', 'hostloc.net', 'www.hostloc.net'],
        'preferred_strategies': ['jina', 'opencli_browser', 'playwright'],
        'cleanup_profile': 'forum_thread',
    },
    'nodeseek': {
        'name': 'NodeSeek',
        'domains': ['nodeseek.com', 'www.nodeseek.com'],
        'preferred_strategies': ['jina', 'opencli_browser', 'playwright'],
        'cleanup_profile': 'forum_thread',
    },
    'linuxdo': {
        'name': 'LINUX DO',
        'domains': ['linux.do'],
        'preferred_strategies': ['jina', 'opencli_browser', 'playwright'],
        'cleanup_profile': 'forum_thread',
    },
    'lowendtalk': {
        'name': 'LowEndTalk',
        'domains': ['lowendtalk.com', 'www.lowendtalk.com'],
        'preferred_strategies': ['jina', 'opencli_browser', 'playwright'],
        'cleanup_profile': 'forum_thread',
    },
    'lowendspirit': {
        'name': 'LowEndSpirit',
        'domains': ['lowendspirit.com', 'www.lowendspirit.com'],
        'preferred_strategies': ['jina', 'opencli_browser', 'playwright'],
        'cleanup_profile': 'forum_thread',
    },
    'reddit': {
        'name': 'Reddit',
        'domains': ['reddit.com', 'www.reddit.com', 'old.reddit.com'],
        'preferred_strategies': ['jina', 'opencli_browser', 'playwright'],
        'cleanup_profile': 'generic',
    },
    'reuters': {
        'name': 'Reuters',
        'domains': ['reuters.com', 'www.reuters.com'],
        'preferred_strategies': ['opencli_browser', 'jina', 'playwright', 'firecrawl'],
        'cleanup_profile': 'generic',
    },
    'hkexnews': {
        'name': 'HKEXnews',
        'domains': ['hkexnews.hk', 'www.hkexnews.hk', 'www1.hkexnews.hk', 'www2.hkexnews.hk'],
        'preferred_strategies': ['jina', 'opencli_browser', 'playwright'],
        'cleanup_profile': 'generic',
    },
    'sec': {
        'name': 'SEC EDGAR',
        'domains': ['sec.gov', 'www.sec.gov'],
        'preferred_strategies': ['jina', 'opencli_browser', 'playwright'],
        'cleanup_profile': 'generic',
    },
    'cls': {
        'name': '财联社',
        'domains': ['cls.cn', 'www.cls.cn'],
        'preferred_strategies': ['jina', 'opencli_browser', 'playwright'],
        'cleanup_profile': 'generic',
    },
    'eastmoney': {
        'name': '东方财富',
        'domains': ['eastmoney.com', 'finance.eastmoney.com', 'biz.eastmoney.com', 'emweb.securities.eastmoney.com', 'data.eastmoney.com', 'guba.eastmoney.com', 'quote.eastmoney.com', 'caifuhao.eastmoney.com'],
        'preferred_strategies': ['playwright', 'jina', 'opencli_browser'],
        'cleanup_profile': 'finance_stock',
    },
    'sinafinance': {
        'name': '新浪财经',
        'domains': ['finance.sina.com.cn', 'vip.stock.finance.sina.com.cn', 'money.finance.sina.com.cn', 'stock.finance.sina.com.cn', 'cj.sina.cn', 'finance.sina.cn'],
        'preferred_strategies': ['jina', 'opencli_browser', 'playwright'],
        'cleanup_profile': 'finance_stock',
    },
    'wallstreetcn': {
        'name': '华尔街见闻',
        'domains': ['wallstreetcn.com'],
        'preferred_strategies': ['jina', 'opencli_browser', 'playwright'],
        'cleanup_profile': 'generic',
    },
    'eniu': {
        'name': '亿牛网',
        'domains': ['eniu.com'],
        'preferred_strategies': ['playwright', 'opencli_browser', 'jina'],
        'cleanup_profile': 'finance_stock',
    },
    'xueqiu': {
        'name': '雪球',
        'domains': ['xueqiu.com', 'stockn.xueqiu.com'],
        'preferred_strategies': ['playwright', 'jina', 'opencli_browser'],
        'cleanup_profile': 'finance_stock',
    },
}


def identify_platform(url: str) -> dict:
    """
    Return platform info for *url*.

    Returns dict with keys: id, name, domains, preferred_strategies, cleanup_profile.
    Falls back to 'generic' for unknown domains.
    """
    domain = urlparse(url).netloc.lower()

    for pid, info in PLATFORMS.items():
        for d in info['domains']:
            if _domain_matches(domain, d):
                return {'id': pid, **info}

    return {
        'id': 'generic',
        'name': '通用网站',
        'domains': [],
        'preferred_strategies': ['firecrawl', 'opencli_browser', 'jina', 'playwright'],
        'cleanup_profile': 'generic',
    }


def _domain_matches(domain: str, candidate: str) -> bool:
    candidate = candidate.lower()
    return domain == candidate or domain.endswith(f'.{candidate}')
