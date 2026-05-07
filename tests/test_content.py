import unittest

from scripts.content import postprocess_content
from scripts.platforms import identify_platform


X_RAW = """Title: plantegg on X: "基础技术的力量：两个 Linux几十年没改过的内核参数" / X

URL Source: https://x.com/plantegg/status/2044321931944497364

Published Time: Thu, 16 Apr 2026 03:26:02 GMT

Markdown Content:
## Article

## Conversation

[![Image 1: Image](https://pbs.twimg.com/media/HFxrpYZWgAAWyq4?format=jpg&name=small)](https://x.com/plantegg/article/2044321931944497364/media/2043626689586954240)

基础技术的力量：两个 Linux几十年没改过的内核参数

数据库 crash 重启了，业务却迟迟恢复不了。

监控报警一片红，业务方打来电话，DBA 确认数据库早就正常了。那问题出在哪？

tcp_keepalive_time，默认 7200 秒，连接空闲 2 小时后才发第一个探活包。

tcp_retries2，默认 15 次，重传约 924 秒后才放弃连接。
"""


NODESEEK_RAW = """Title: 【拒绝“送中”与 IP 黑名单】IP-Sentinel 分布式哨兵系统v3.1.0重装上阵！让你的小鸡完美伪装成“当地人”

URL Source: https://www.nodeseek.com/post-683468-1

Markdown Content:
# 【拒绝“送中”与 IP 黑名单】IP-Sentinel 分布式哨兵系统v3.1.0重装上阵！让你的小鸡完美伪装成“当地人”

**[![Image 1: logo](https://www.nodeseek.com/static/image/favicon/android-chrome-192x192.png)NodeSeek beta](https://www.nodeseek.com/)**
*   [日常](https://www.nodeseek.com/categories/daily)

[search for post](javascript:void(0))[search for people](javascript:void(0))[use google search](javascript:void(0))

#### 所有版块

# [【拒绝“送中”与 IP 黑名单】IP-Sentinel 分布式哨兵系统v3.1.0重装上阵！让你的小鸡完美伪装成“当地人”](https://www.nodeseek.com/post-683468-1)

[![Image 2: gudaomao](https://www.nodeseek.com/avatar/27010.png)](https://www.nodeseek.com/space/27010 "gudaomao")

[gudaomao](https://www.nodeseek.com/space/27010)楼主

5days ago edited 19h 17min ago in [技术](https://www.nodeseek.com/categories/tech)

[#0](https://www.nodeseek.com/post-683468-1#0)

主楼第一段

主楼第二段

1[2](https://www.nodeseek.com/post-683468-2)[3](https://www.nodeseek.com/post-683468-3)[..23](https://www.nodeseek.com/post-683468-23)[](https://www.nodeseek.com/post-683468-2)

*   [![Image 7: Murasaki](https://www.nodeseek.com/avatar/1.png)](https://www.nodeseek.com/space/1 "Murasaki") [Murasaki](https://www.nodeseek.com/space/1) 1day ago [#132](https://www.nodeseek.com/post-683468-1#132)
审计了一下写的没啥问题很有水平

登录 或者 注册 后评论.

你好啊，陌生人!

快捷功能区

推荐阅读
"""


LINUXDO_RAW = """Title: codex app 启动问题

URL Source: https://linux.do/t/topic/2115948

Published Time: 2026-05-05T15:27:33+00:00

Markdown Content:
*   [Topics](https://linux.do/latest "All topics")
*   [Upcoming events](https://linux.do/upcoming-events "Upcoming events")
*   [开发调优](https://linux.do/c/develop/4 "此版块包含开发、测试、调试、部署、优化、安全等方面的内容。")
*   [人工智能](https://linux.do/tag/444-tag/444)

Default

**真诚**、**友善**、**团结**、**专业**，共建你我引以为荣之社区。[《社区准则》](https://linux.do/guidelines)

1 / 3

May 5

## post by ve99 19 mins ago

[![Image 1](https://cdn.ldstatic.com/user_avatar/linux.do/ve99/48/1748117_2.png)](https://linux.do/u/ve99)

佬们，今天想试试codex app，从微软商店下载安装后，启动失败。

我看到 .codex文件夹里也自动创建了 sqlite 文件夹

点击重新加载后

[![Image 2](https://cdn.ldstatic.com/user_avatar/linux.do/coee/48/1079432_2.png)](https://linux.do/u/Coee "Coee")

## post by Coee 15 mins ago

[![Image 3](https://cdn.ldstatic.com/user_avatar/linux.do/coee/48/1079432_2.png)](https://linux.do/u/coee)

Solution

重启系统试试

## post by ve99 4 mins ago

[![Image 4](https://cdn.ldstatic.com/user_avatar/linux.do/ve99/48/1748117_2.png)](https://linux.do/u/ve99)

装了之后，重启系统，的确有用，谢谢佬！！！

### Related topics

Topic list, column headers with buttons are sortable.
"""


V2EX_RAW = """Title: [AI 中转站 / 福利贴]OneXModel 推广拉新，限时回帖送$，稳定、靠谱、好用～

URL Source: https://www.v2ex.com/t/1210308

Published Time: 2026-05-05T07:48:58Z

Markdown Content:
# [AI 中转站 / 福利贴]OneXModel 推广拉新，限时回帖送$，稳定、靠谱、好用～ - V2EX

[Home](https://www.v2ex.com/)[Sign Up](https://www.v2ex.com/signup)[Sign In](https://www.v2ex.com/signin)

如果想在 V2EX 获得更好的推广效果，欢迎了解 PRO 会员机制：

[https://www.v2ex.com/pro/about](https://www.v2ex.com/pro/about)

Promoted by [laojuelv](https://www.v2ex.com/member/laojuelv)

[V2EX](https://www.v2ex.com/)›[推广](https://www.v2ex.com/go/promotions)

# [AI 中转站 / 福利贴]OneXModel 推广拉新，限时回帖送$，稳定、靠谱、好用～

[Robot2012](https://www.v2ex.com/member/Robot2012) ·

PRO

 · 7h 7m ago · 404 views

## 我们是谁？

OneXModel 是一个聚合 AI 算力平台。

## 为什么选择我们？

*   `充值汇率：1 RMB = 1 USD`
*   `最低 1 元起充`

[![Image 4](https://i.v2ex.co/97YkBQdO.png)](https://1xm.ai/)

[AI](https://www.v2ex.com/tag/AI)[算力](https://www.v2ex.com/tag/%E7%AE%97%E5%8A%9B)

17 replies **•**2026-05-05 22:55:57 +08:00

![Image 6: Lknifeo](https://cdn.v2ex.com/gravatar/d373fb8f09781b96295e1e740343a34d?s=48&d=retro)1

**[Lknifeo](https://www.v2ex.com/member/Lknifeo)**6h 21m ago

2192

谢谢老板!!!

![Image 7: qq05629](https://cdn.v2ex.com/avatar/cd12/fcfa/215345_normal.png?m=1586077636)2

**[qq05629](https://www.v2ex.com/member/qq05629)**2h 40m ago

ID: 2211, 多谢老板, 我的邀请码: ti8n

![Image 8: HelpfulUser](https://cdn.v2ex.com/avatar/test.png)3

**[HelpfulUser](https://www.v2ex.com/member/HelpfulUser)**1h 15m ago

实测 Claude Code 的中转延迟在晚高峰会升到 4s 左右，写代码时体感明显。

通过 Atom Feed 订阅

»More Recent Topics
"""


ZHIHU_QUESTION_RAW = """[![](https://pica.zhimg.com/v2-avatar.jpg?source=1def8aca)KYC认证](/people/kpdh-14)

[

AIGC

](//www.zhihu.com/topic/26215901)

# claude怎么订阅最便宜？

claude怎么订阅最便宜？

关注者

**292**

被浏览

**366,488**

#### 3 个回答

[![麻小辣](https://pica.zhimg.com/v2-aa3a87e7b61158e486ea2cef40d688b3_l.jpg?source=1def8aca)](//www.zhihu.com/people/gong-ji-xin-73)

[麻小辣](//www.zhihu.com/people/gong-ji-xin-73)

美好如你，岁月如初。

尼日利亚区的Claude订阅是全球最低价，我不允许还有人不知道这个信息差。

![](<data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg'></svg>>)

1. 第一步注册尼日利亚 Apple ID

[![孤飞](https://picx.zhimg.com/v2-5ea0749e6af0956f1e9fb6981c396b07_l.jpg?source=1def8aca)](//www.zhihu.com/people/onefly_eth)

[孤飞](//www.zhihu.com/people/onefly_eth)

WEB3 会炼丹的白嫖区答主 vlink.cc/tosky

开门见山——Claude Pro 在苹果尼日利亚区的订阅价只要 88 元人民币左右。

查看剩余 48 条回答

下载知乎客户端

大家都在搜
"""


class PlatformIdentificationTests(unittest.TestCase):
    def test_identify_x_urls_as_explicit_x_platform(self):
        for url in (
            "https://x.com/plantegg/status/2044321931944497364",
            "https://twitter.com/plantegg/status/2044321931944497364",
        ):
            with self.subTest(url=url):
                platform = identify_platform(url)
                self.assertEqual(platform["id"], "x")
                self.assertEqual(platform["name"], "X")
                self.assertEqual(platform["preferred_strategies"][0], "jina")

    def test_identify_linuxdo_as_explicit_platform(self):
        platform = identify_platform("https://linux.do/t/topic/2115948")
        self.assertEqual(platform["id"], "linuxdo")
        self.assertEqual(platform["name"], "LINUX DO")

    def test_identify_v2ex_as_explicit_platform_and_not_x(self):
        for url in (
            "https://www.v2ex.com/",
            "https://www.v2ex.com/t/1210308",
        ):
            with self.subTest(url=url):
                platform = identify_platform(url)
                self.assertEqual(platform["id"], "v2ex")
                self.assertEqual(platform["name"], "V2EX")

    def test_identify_reddit_as_explicit_platform(self):
        platform = identify_platform("https://www.reddit.com/r/OpenAI/comments/abc123/example/")
        self.assertEqual(platform["id"], "reddit")
        self.assertEqual(platform["name"], "Reddit")


class ContentCleanupTests(unittest.TestCase):
    def test_x_postprocessing_removes_jina_wrapper_sections(self):
        result = postprocess_content(
            X_RAW,
            "https://x.com/plantegg/status/2044321931944497364",
            {"id": "x", "name": "X", "preferred_strategies": ["jina", "playwright", "firecrawl"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# 基础技术的力量：两个 Linux几十年没改过的内核参数", result["content"])
        self.assertIn("## 正文", result["content"])
        self.assertIn("tcp_keepalive_time", result["content"])
        self.assertIn("tcp_retries2", result["content"])
        self.assertNotIn("## Article", result["content"])
        self.assertNotIn("## Conversation", result["content"])
        self.assertNotIn("Published Time:", result["content"])

    def test_nodeseek_postprocessing_strips_footer_and_login_noise(self):
        result = postprocess_content(
            NODESEEK_RAW,
            "https://www.nodeseek.com/post-683468-1",
            {"id": "nodeseek", "name": "NodeSeek", "preferred_strategies": ["jina", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("## 主楼", result["content"])
        self.assertIn("主楼第一段", result["content"])
        self.assertIn("## 回复", result["content"])
        self.assertNotIn("登录 或者 注册", result["content"])
        self.assertNotIn("你好啊，陌生人", result["content"])
        self.assertNotIn("快捷功能区", result["content"])
        self.assertNotIn("推荐阅读", result["content"])

    def test_nodeseek_filters_obvious_low_information_replies(self):
        raw = """Title: 测试帖子

URL Source: https://www.nodeseek.com/post-123-1

Markdown Content:
# [测试帖子](https://www.nodeseek.com/post-123-1)

[tester](https://www.nodeseek.com/space/1)楼主

1day ago in [技术](https://www.nodeseek.com/categories/tech)

[#0](https://www.nodeseek.com/post-123-1#0)

这里是主楼正文

*   [![Image 1: user1](https://www.nodeseek.com/avatar/1.png)](https://www.nodeseek.com/space/2 "user1") [user1](https://www.nodeseek.com/space/2) 1day ago [#1](https://www.nodeseek.com/post-123-1#1)
支持

*   [![Image 2: user2](https://www.nodeseek.com/avatar/2.png)](https://www.nodeseek.com/space/3 "user2") [user2](https://www.nodeseek.com/space/3) 1day ago [#2](https://www.nodeseek.com/post-123-1#2)
有人实测过吗

*   [![Image 3: user3](https://www.nodeseek.com/avatar/3.png)](https://www.nodeseek.com/space/4 "user3") [user3](https://www.nodeseek.com/space/4) 1day ago [#3](https://www.nodeseek.com/post-123-1#3)
占领前排，支持大佬新作

*   [![Image 4: user4](https://www.nodeseek.com/avatar/4.png)](https://www.nodeseek.com/space/5 "user4") [user4](https://www.nodeseek.com/space/5) 1day ago [#4](https://www.nodeseek.com/post-123-1#4)
大概 4 天左右 Google 定位恢复了，但是 Gemini 还没解锁
"""
        result = postprocess_content(
            raw,
            "https://www.nodeseek.com/post-123-1",
            {"id": "nodeseek", "name": "NodeSeek", "preferred_strategies": ["jina", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertNotIn("支持", result["content"])
        self.assertNotIn("占领前排", result["content"])
        self.assertIn("有人实测过吗", result["content"])
        self.assertIn("Gemini 还没解锁", result["content"])

    def test_linuxdo_topic_postprocessing_extracts_thread_and_replies(self):
        result = postprocess_content(
            LINUXDO_RAW,
            "https://linux.do/t/topic/2115948",
            {"id": "linuxdo", "name": "LINUX DO", "preferred_strategies": ["jina", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# codex app 启动问题", result["content"])
        self.assertIn("**楼主**: ve99", result["content"])
        self.assertIn("## 主楼", result["content"])
        self.assertIn("微软商店下载安装后，启动失败", result["content"])
        self.assertIn("## 回复", result["content"])
        self.assertIn("Coee | 15 mins ago", result["content"])
        self.assertIn("重启系统试试", result["content"])
        self.assertNotIn("### Related topics", result["content"])
        self.assertNotIn("社区准则", result["content"])
        self.assertNotIn("Solution", result["content"])

    def test_v2ex_topic_postprocessing_extracts_main_post_and_filters_thanks_reply(self):
        result = postprocess_content(
            V2EX_RAW,
            "https://www.v2ex.com/t/1210308",
            {"id": "v2ex", "name": "V2EX", "preferred_strategies": ["jina", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# [AI 中转站 / 福利贴]OneXModel 推广拉新，限时回帖送$，稳定、靠谱、好用～", result["content"])
        self.assertIn("**楼主**: Robot2012", result["content"])
        self.assertIn("## 主楼", result["content"])
        self.assertIn("OneXModel 是一个聚合 AI 算力平台", result["content"])
        self.assertIn("## 回复", result["content"])
        self.assertIn("HelpfulUser | 1h 15m ago | #3", result["content"])
        self.assertIn("Claude Code 的中转延迟在晚高峰会升到 4s 左右", result["content"])
        self.assertNotIn("Promoted by", result["content"])
        self.assertNotIn("谢谢老板", result["content"])
        self.assertNotIn("通过 Atom Feed 订阅", result["content"])

    def test_zhihu_question_postprocessing_keeps_only_answers(self):
        result = postprocess_content(
            ZHIHU_QUESTION_RAW,
            "https://www.zhihu.com/question/10434775822",
            {"id": "zhihu", "name": "知乎", "preferred_strategies": ["firecrawl", "jina", "opencli_browser", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# claude怎么订阅最便宜？", result["content"])
        self.assertIn("## 回答", result["content"])
        self.assertIn("1. 麻小辣", result["content"])
        self.assertIn("2. 孤飞", result["content"])
        self.assertIn("尼日利亚区的Claude订阅是全球最低价", result["content"])
        self.assertIn("Claude Pro 在苹果尼日利亚区的订阅价只要 88 元人民币左右", result["content"])
        self.assertNotIn("关注者", result["content"])
        self.assertNotIn("被浏览", result["content"])
        self.assertNotIn("查看剩余", result["content"])
        self.assertNotIn("下载知乎客户端", result["content"])
        self.assertNotIn("大家都在搜", result["content"])
        self.assertNotIn("美好如你，岁月如初。", result["content"])
        self.assertNotIn("WEB3 会炼丹的白嫖区答主", result["content"])
        self.assertNotIn("data:image", result["content"])


if __name__ == "__main__":
    unittest.main()
