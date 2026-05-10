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


CNINFO_PDF_RAW = """Title: 1224639992.PDF

URL Source: https://static.cninfo.com.cn/finalpage/2025-09-05/1224639992.PDF

Published Time: Thu, 04 Sep 2025 13:08:26 GMT

Number of Pages: 12

Markdown Content:
# 证券代码： 688639 证券简称：华恒生物 公告编号： 2025 -034

# 安徽华恒生物科技股份有限公司

# 第四届 董事会第 二十三 次会议决议 公告

本公司董事会及全体董事保证本公告内容不存在任何虚假记载、误导性陈述或者重大遗漏，并对其内容的真实性、准确性和完整性承担法律责任。

一、董事会会议召开情况

安徽华恒生物科技股份有限公司（以下简称 “公司 ”）第四届董事会第二十三次会议于 2025 年 9 月 4 日在公司会议室以现场结合通讯方式召开。

二、董事会会议审议情况

（一）审议通过《关于公司发行 H 股股票并在香港联合交易所有限公司上市的议案》

为深入推进公司全球化发展战略，提升品牌影响力与核心竞争力，公司拟发行境外上市外资股（H 股）股票并申请在香港联合交易所有限公司主板挂牌上市。
"""


CNINFO_LIST_RAW = """Title: 巨潮资讯网

URL Source: https://www.cninfo.com.cn/new/commonUrl?url=disclosure/list/notice

Markdown Content:
![Image 1](https://static.cninfo.com.cn/new/assets/image/graph_icon.png)共 768 家 1314 条

[301337](https://www.cninfo.com.cn/new/disclosure/stock?stockCode=301337&orgId=gfbj0838234)[亚华电子](https://www.cninfo.com.cn/new/disclosure/stock?stockCode=301337&orgId=gfbj0838234)[东吴证券股份有限公司关于山东亚华电子股份有限公司2025年度持续督导跟踪报告](https://www.cninfo.com.cn/new/disclosure/detail?stockCode=301337&announcementId=1225283886&orgId=gfbj0838234&announcementTime=2026-05-08)2026-05-08 03:42
[300880](https://www.cninfo.com.cn/new/disclosure/stock?stockCode=300880&orgId=9900039789)[迦南智能](https://www.cninfo.com.cn/new/disclosure/stock?stockCode=300880&orgId=9900039789)[关于重大经营合同中标的公告](https://www.cninfo.com.cn/new/disclosure/detail?stockCode=300880&announcementId=1225283887&orgId=9900039789&announcementTime=2026-05-08)2026-05-08 03:36
[000020](https://www.cninfo.com.cn/new/disclosure/stock?stockCode=000020&orgId=gssz0000020)[深华发Ａ](https://www.cninfo.com.cn/new/disclosure/stock?stockCode=000020&orgId=gssz0000020)[涉及诉讼、仲裁的公告](https://www.cninfo.com.cn/new/disclosure/detail?stockCode=000020&announcementId=1225283137&orgId=gssz0000020&announcementTime=2026-05-07)2026-05-07 16:00
"""


SSE_PDF_RAW = """Title: 证券代码：002669 证券简称：康达新材 公告编号：2015-040

URL Source: https://big5.sse.com.cn/site/cht/www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2025-10-10/601700_20251010_GVF1.pdf

Published Time: Thu, 09 Oct 2025 07:45:21 GMT

Number of Pages: 3

Markdown Content:
证券代码 ：601700 证券简称 ：风范股份 公告编号 ：2025-055

# 常熟风范电力设备股份有限公司

# 关于以集中竞价方式回购股份的进展公告

本公司董事会及全体董事保证本公告内容不存在任何虚假记载、误导性陈述或者重大遗漏，并对其内容的真实性、准确性和完整性承担个别及连带责任。

重要内容提示：

回购方案首次披露日 2024 年 11 月 13 日

一、回购股份的基本情况

常熟风范电力设备股份有限公司（以下简称 “公司 ”）于2024 年11 月12 日召开第六届董事会第七次会议。

二、回购股份的进展情况

截至 2025 年9月30 日，公司通过回购专用证券账户以集中竞价交易方式实施股份回购，回购股份数量为 26,814,100 股，占公司目前总股本的 2.35%。

三、其他事项

公司将严格按照《上市公司股份回购规则》等相关规定及时履行信息披露义务，敬请广大投资者注意投资风险。
"""


SSE_LIST_RAW = """Title: 公司公告 | 上海证券交易所科创板

URL Source: https://star.sse.com.cn/star/disclosure/listannouncement/

Markdown Content:
*   _2026-05-08_[688001 : 华兴源创：关于实施“华兴转债” 赎回暨摘牌的第一次提示性公告](https://star.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-05-08/688001_20260508_G6EM.pdf)
*   _2026-05-08_[688002 : 关于参加2026年山东辖区上市公司投资者网上集体接待日活动的公告](https://star.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-05-08/688002_20260508_ET7E.pdf)
*   _2026-05-08_[688022 : 关于公司诉讼达成和解及撤诉的公告](https://star.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-05-08/688022_20260508_A9HZ.pdf)
*   _2026-05-08_[688022 : 股票交易异常波动公告](https://star.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-05-08/688022_20260508_F5E3.pdf)
"""


REUTERS_ARTICLE_RAW = """Title: RBC lifts S&P 500 year-end target to 7,900 on AI optimism | Reuters

URL Source: https://www.reuters.com/business/finance/rbc-lifts-sp-500-year-end-target-7900-ai-optimism-2026-05-08/

Markdown Content:
![Illustration shows message reading "AI artificial intelligence", keyboard and robot hands](https://www.reuters.com/resizer/v2/SMAEMXCSQFIIDDDDWMGIP4YF5E.jpg)

A message reading "AI artificial intelligence", a keyboard, and robot hands are seen in this illustration taken January 27, 2025. REUTERS/Dado Ruvic/Illustration/File Photo [Purchase Licensing Rights, opens new tab](https://www.reutersconnect.com/item/example)

May 8 (Reuters) - RBC Capital Markets raised its year-end target for the S&P 500 [(.SPX), opens new tab](https://www.reuters.com/markets/quote/.SPX) to 7,900 from 7,750 on Friday, citing resilient earnings growth and continued strength in artificial intelligence-linked sectors.

The Canadian brokerage's new target implies a 7.7% upside from the benchmark index's Thursday close of 7,335.66.

The Week in Breakingviews newsletter offers insights and ideas from Reuters' global financial commentary team. Sign up [here.](/newsletters/the-week-in-breakingviews/)

U.S. equities have rallied to hit record highs in recent weeks as enthusiasm around AI-related investment and expectations of solid profit growth continue to support investor appetite.

Advertisement · Scroll to continue

The S&P 500 [(.SPX), opens new tab](https://www.reuters.com/markets/quote/.SPX) posted its biggest monthly percentage gain since November 2020 last month.

Reporting by Rashika Singh in Bengaluru; Editing by Sumana Nandy and Sonia Cheema

Our Standards: [The Thomson Reuters Trust Principles., opens new tab](https://www.thomsonreuters.com/en/about-us/trust-principles.html)

[Purchase Licensing Rights](https://www.reutersagency.com/en/licensereuterscontent/)

## Read Next

-   39 mins ago[Financecategory](/business/finance/)

    [Commerzbank plans 3,000 job cuts, raises targets as it fends off UniCredit takeover](/business/finance/commerzbank-upgrades-targets-it-fends-off-unicredit-takeover-2026-05-08/)
"""


REUTERS_MARKETS_RAW = """Title: Global Market Headlines | Breaking Stock Market News | Reuters

URL Source: https://www.reuters.com/markets/

Markdown Content:
# Markets

[Official Data Partner](https://www.lseg.com/en)

-   US
-   Europe
-   Asia Pacific

[Morning Bid: Markets cling on as ceasefire is tested](/world/china/global-markets-view-europe-2026-05-08/)

· 1:55 PM GMT+8 · Updated 1 hour ago

The German share price index DAX graph is pictured at the stock exchange in Frankfurt, Germany, May 7, 2026. REUTERS/staff

A look at the day ahead in European and global markets from Tom Westbrook

[](/authors/jamie-mcgeever/)[Trading Day: Markets draw breath Jamie McGeever](https://www.reuters.com/commentary/reuters-open-interest/global-markets-trading-day-graphic-2026-05-07/)

[](/authors/gavin-maguire/)[Seven markets to track if peace breaks out in the Middle East Gavin Maguire](https://www.reuters.com/markets/seven-markets-track-if-peace-breaks-out-middle-east-2026-05-08/)

## Markets Performance

[Official Data Partner](https://www.lseg.com/en)

### Commodities

Gold

4,717.50

### Stocks

S&P 500

7,337.11

## [Asian Markets](/markets/asia/)

-   ANALYSIS[Japan bets on Washington, BOJ for extra punch in yen battle](https://www.reuters.com/world/asia-pacific/japan-bets-washington-boj-extra-punch-yen-battle-2026-05-08/)

    2:49 PM GMT+8

-   [category](/world/)[China's April bank lending seen plunging amid soft credit demand: Reuters poll](https://www.reuters.com/world/asia-pacific/chinas-april-bank-lending-seen-plunging-amid-soft-credit-demand-2026-05-08/)

    1:27 PM GMT+8

## [European Markets](/markets/europe/)

-   [Businesscategory](/business/)[ECB's Lagarde is sceptical of euro stablecoins](https://www.reuters.com/business/finance/ecbs-lagarde-is-sceptical-euro-stablecoins-2026-05-08/)

    3:02 PM GMT+8

## [U.S. Markets](/markets/us/)

-   [Businesscategory](/business/)[RBC lifts S&P 500 year-end target to 7,900 on AI optimism](https://www.reuters.com/business/finance/rbc-lifts-sp-500-year-end-target-7900-ai-optimism-2026-05-08/)

    1:46 PM GMT+8

Notice of Your Privacy Choices
"""


HKEX_TITLE_SEARCH_RAW = """Title: Listed Company Information Title Search

URL Source: https://www1.hkexnews.hk/search/titlesearch.xhtml?category=0&lang=EN&market=SEHK&stockId=1000113244

Markdown Content:
Release Time: 06/05/2026 16:50 | Stock Code: 09869 | Stock Short Name: HELENS | Document: Monthly Returns [Monthly Return of Equity Issuer on Movements in Securities for the month ended 30 April 2026](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0506/2026050601208.pdf) (66KB) |
| Release Time: 22/04/2026 17:18 | Stock Code: 09869 | Stock Short Name: HELENS | Document: Announcements and Notices - [Change in Directors or of Important Executive Functions or Responsibilities] [RETIREMENT OF EXECUTIVE DIRECTOR AND PROPOSED ELECTION OF EXECUTIVE DIRECTOR](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0422/2026042200963.pdf) (437KB) |
| Release Time: 31/03/2026 21:32 | Stock Code: 09869 | Stock Short Name: HELENS | Document: Announcements and Notices - [Final Results / Dividend or Distribution / Closure of Books or Change of Book Closure Period] [ANNOUNCEMENT OF ANNUAL RESULTS FOR THE YEAR ENDED DECEMBER 31, 2025](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0331/2026033103201.pdf) (566KB) |
"""


HKEX_PDF_RAW = """Title: 2026040800057.pdf

URL Source: https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0408/2026040800057.pdf

Published Time: Tue, 07 Apr 2026 23:00:48 GMT

Number of Pages: 70

Markdown Content:
# THIS CIRCULAR IS IMPORTANT AND REQUIRES YOUR IMMEDIATE ATTENTION

(Stock Code: 1038)

CONNECTED TRANSACTION AND MAJOR TRANSACTION

DISPOSAL OF UK POWER NETWORKS

AND NOTICE OF SPECIAL GENERAL MEETING

A letter from the Board to the Shareholders is set out on pages 15 to 28 of this circular.

8 April 2026

## LETTER FROM THE BOARD

The Board announces that the disposal constitutes a connected transaction and a major transaction under the Listing Rules.

The notice convening the SGM is set out on pages N-1 to N-3 of this circular.
"""


SEC_BROWSE_RAW = """Title: EDGAR Entity Landing Page

URL Source: https://www.sec.gov/edgar/browse/?CIK=320193&owner=exclude&action=getcompany

Markdown Content:
144[Report of proposed sale of securities Open document](https://www.sec.gov/Archives/edgar/data/0000320193/000192109426000446/xsl144X01/primary_doc.xml)Click to Open document[Filing Open filing](https://www.sec.gov/Archives/edgar/data/0000320193/000192109426000446/0001921094-26-000446-index.htm)Click to Open filing 2026-05-06
10-Q[Quarterly report [Sections 13 or 15(d)] Open document](https://www.sec.gov/ix?doc=/Archives/edgar/data/0000320193/000032019326000013/aapl-20260328.htm)Click to Open document[Filing Open filing](https://www.sec.gov/Archives/edgar/data/0000320193/000032019326000013/0000320193-26-000013-index.htm)Click to Open filing 2026-05-01[2026-03-28 View all with same reporting date](https://www.sec.gov/edgar/browse/?CIK=320193&owner=exclude&action=getcompany#)
8-K[Current report Open document](https://www.sec.gov/ix?doc=/Archives/edgar/data/0000320193/000032019326000011/aapl-20260430.htm)Click to Open document[Filing Open filing](https://www.sec.gov/Archives/edgar/data/0000320193/000032019326000011/0000320193-26-000011-index.htm)Click to Open filing

*   **2.02** - Results of Operations and Financial Condition
*   **9.01** - Financial Statements and Exhibits 2026-04-30
"""


SEC_INDEX_RAW = """Title: EDGAR Filing Documents for 0000320193-26-000013

URL Source: https://www.sec.gov/Archives/edgar/data/0000320193/000032019326000013/0000320193-26-000013-index.htm

Markdown Content:
Filing Date

2026-05-01

Accepted

2026-05-01 06:01:00

Documents

61

Period of Report

2026-03-28

Document Format Files

| Seq | Description | Document | Type | Size |
| --- | --- | --- | --- | --- |
| 1 | 10-Q | [aapl-20260328.htm](https://www.sec.gov/ix?doc=/Archives/edgar/data/320193/000032019326000013/aapl-20260328.htm)iXBRL | 10-Q | 999810 |
| 2 | EX-31.1 | [a10-qexhibit31103282026.htm](https://www.sec.gov/Archives/edgar/data/320193/000032019326000013/a10-qexhibit31103282026.htm) | EX-31.1 | 10524 |
| 3 | EX-31.2 | [a10-qexhibit31203282026.htm](https://www.sec.gov/Archives/edgar/data/320193/000032019326000013/a10-qexhibit31203282026.htm) | EX-31.2 | 10563 |

Data Files

| Seq | Description | Document | Type | Size |
| --- | --- | --- | --- | --- |
| 5 | XBRL TAXONOMY EXTENSION SCHEMA DOCUMENT | [aapl-20260328.xsd](https://www.sec.gov/Archives/edgar/data/320193/000032019326000013/aapl-20260328.xsd) | EX-101.SCH | 35423 |
"""


CLS_HOME_RAW = """Title: 财联社-主流财经新闻集团和财经通讯社-cls.cn

URL Source: https://www.cls.cn/

Markdown Content:
# 财联社-主流财经新闻集团和财经通讯社-cls.cn

[关于我们](https://www.cls.cn/our?nav=our)[网站声明](https://www.cls.cn/our?nav=copyright)[联系方式](https://www.cls.cn/our?nav=contact)

注册|登录

## [首页](https://www.cls.cn/)## [电报](https://www.cls.cn/telegraph)## [话题](https://www.cls.cn/subject)

[上证指数](https://www.cls.cn/ind?code=sh000001)
[4179.95](https://www.cls.cn/ind?code=sh000001)

10:27[【数据看盘】北向资金联手游资抢筹商业航天人气股 多路资金激烈博弈光迅科技](https://www.cls.cn/detail/2366221)

[①商业航天概念集体爆发，航天发展涨停，国泰海通证券武汉紫阳东路营业部买入3.06亿。](https://www.cls.cn/detail/2366221)

头条[特朗普称中美元首会谈将按计划举行，外交部回应](https://www.cls.cn/detail/2366051)

澎湃新闻 5月8日 07:43

头条[三部门联合印发《智能体规范应用与创新发展实施意见》](https://www.cls.cn/detail/2366263)

财联社 5月8日 10:26

[冲刺7900点！RBC上调标普500年底目标价 看好AI行业前景](https://www.cls.cn/detail/2366149)

财联社电报 2026.05.08 星期五

[11:43 财联社5月8日电，据报道，DeepSeek拟募资最高500亿元人民币，这将成为中国人工智能公司有史以来最大的一轮融资。](https://www.cls.cn/detail/2366381)

热门板块
"""


CLS_DETAIL_RAW = """Title: 冲刺7900点！RBC上调标普500年底目标价 看好AI行业前景

URL Source: https://www.cls.cn/detail/2366149

Markdown Content:
# 冲刺7900点！RBC上调标普500年底目标价 看好AI行业前景

[关于我们](https://www.cls.cn/our?nav=our)[网站声明](https://www.cls.cn/our?nav=copyright)[联系方式](https://www.cls.cn/our?nav=contact)

冲刺7900点！RBC上调标普500年底目标价 看好AI行业前景

原创

[环球市场情报](https://www.cls.cn/subject/1556)

2026-05-08 09:27 星期五

财联社 黄君芝

①加拿大皇家银行资本市场将标普500指数的年底目标价从7750点上调至7900点，因盈利增长强劲和AI相关行业持续走强；
②RBC的看涨立场与摩根大通和巴克莱银行等华尔街主要券商的类似举措相呼应。

**财联社5月8日讯（编辑 黄君芝）**加拿大皇家银行资本市场（RBC Capital Markets）周五将标普500指数的年底目标价从7750点上调至7900点，理由是盈利增长强劲，以及人工智能（AI）相关行业持续走强。

最新目标价意味着标普500还能较当前水平上涨约7.6%。

近几周来，美国股市持续上涨，屡创新高，投资者对人工智能相关投资的热情以及对稳健利润增长的预期继续支撑着他们的投资意愿。

根据RBC策略师们的说法，科技和人工智能相关企业盈利预期上调，以及对人工智能基础设施的强劲需求推动，这些因素共同支撑了市场估值。

收藏

阅 6.96W

我要评论

欢迎您发表有价值的评论

关联话题

[环球市场情报](https://www.cls.cn/subject/1556)

15.46W 人关注

[财联社](https://www.cls.cn/ "财联社") ©2018-2026 上海界面财联社科技股份有限公司 版权所有
"""


EASTMONEY_HOME_RAW = """Title: 财经首页 - 东方财富网

URL Source: https://finance.eastmoney.com/

Published Time: Fri, 08 May 2026 12:07:12 GMT

Markdown Content:
# 财经首页 - 东方财富网

*   [焦点](http://finance.eastmoney.com/yaowen.html)
*   [上市公司](http://finance.eastmoney.com/company.html)

全球时间:北京 05-08 12:07:30 东京 05-08 13:07:30

[上证指数](http://quote.eastmoney.com/unify/r/1.000001)
[4179.95](http://quote.eastmoney.com/unify/r/1.000001)

[段永平买入泡泡玛特](https://finance.eastmoney.com/a/202605073730438926.html "段永平买入泡泡玛特")
[中国长城关联交易骤增](https://finance.eastmoney.com/a/202605083730511151.html "中国长城关联交易骤增")

19:54|[【伟测科技：拟发行不超20亿元可转债用于总部基地等项目】伟测科技(688372.SH)公告称，公司董事会审议通过向不特定对象发行可转换公司债券预案，拟发行总额不超过20亿元。](http://finance.eastmoney.com/a/202605083731725958.html)
19:44|[【DeepSeek拟募资最高500亿元人民币】据报道，DeepSeek拟募资最高500亿元人民币，这将成为中国人工智能公司有史以来最大的一轮融资。](http://finance.eastmoney.com/a/202605083731721875.html)

热门板块
"""


EASTMONEY_ARTICLE_RAW = """Title: 段永平买入泡泡玛特

URL Source: https://finance.eastmoney.com/a/202605073730438926.html

Markdown Content:
# 段永平买入泡泡玛特

[首页](http://finance.eastmoney.com/)

2026-05-07 21:32

来源：证券时报网

收藏

评论

证券时报e公司讯，知名投资人段永平在社交平台发文表示，自己买了一些泡泡玛特（09992.HK），原因是“看懂了一点这个生意”。

他表示，虽然对潮玩行业了解不深，但从品牌、渠道和消费者黏性来看，泡泡玛特已经形成较强的护城河。

有市场人士认为，段永平的表态或将进一步强化市场对消费龙头和IP经济的关注。

责任编辑：123

相关阅读

网友点击
"""


SINAFINANCE_HOME_RAW = """Title: 新浪财经_金融信息服务商

URL Source: https://finance.sina.com.cn/

Markdown Content:
# 新浪财经_金融信息服务商

[新浪首页](http://www.sina.com.cn/)>>[巴菲特股东大会](https://finance.sina.com.cn/zt_d/berkshiream2026/)

*   [股票](http://finance.sina.com.cn/stock/)
*   [基金](http://finance.sina.com.cn/fund/)

[段永平买入泡泡玛特](https://finance.sina.com.cn/stock/companyt/2026-05-07/doc-inhwzvzm2859606.shtml)
[国泰基金投资运作违规被罚](https://finance.sina.com.cn/money/fund/2026-05-08/doc-inhxcusp2275828.shtml)

[环球市场>>](http://finance.sina.com.cn/money/globalindex/)

*   [上证综指](http://finance.sina.com.cn/realstock/company/sh000001/nc.shtml)
*   4179.95

热门资讯

[美军对伊朗实施定点打击伊朗反击](https://finance.sina.com.cn/china/gncj/2026-05-08/doc-inhxxxx1.shtml)
[重仓韩国芯片股，又跑出一只基金黑马，单日大涨12%](https://finance.sina.com.cn/money/fund/2026-05-08/doc-inhxxxx2.shtml)
"""


SINAFINANCE_ARTICLE_RAW = """Title: 国泰基金：投资运作违规被罚 多只产品大幅跑输基准仍高收费

URL Source: https://finance.sina.com.cn/money/fund/2026-05-08/doc-inhxcusp2275828.shtml

Published Time: 2026-05-08T07:41:18+08:00

Markdown Content:
# 国泰基金：投资运作违规被罚 多只产品大幅跑输基准仍高收费_新浪财经_新浪网

*   [新浪首页](http://www.sina.com.cn/)
*   [财经](http://finance.sina.com.cn/)

[基金](http://finance.sina.com.cn/fund/)>正文

# 国泰基金：投资运作违规被罚 多只产品大幅跑输基准仍高收费

国泰基金：投资运作违规被罚 多只产品大幅跑输基准仍高收费

2026年05月08日 07:31 市场资讯

[新浪财经APP](https://finance.sina.com.cn/mobile/comfinanceweb.shtml?source=cjzhengwen04)

来源：面包财经

编者按：公募基金行业在监管“长牙带刺”、推动高质量发展的大背景下，进入了强监管、严问责的时期。

面包财经基于信披数据，分批透视主要基金公司相关事宜。本篇案例为国泰基金。

据近期公告披露，2025年5月，国泰基金因投资运作违规被中国证监会上海监管局采取责令改正的行政监管措施。

除自身合规管理存在漏洞外，国泰基金旗下部分产品同时暴露出业绩低迷等问题。

责任编辑：123

热门评论

加载更多

东方财富
"""


WALLSTREETCN_HOME_RAW = """Title: 华尔街见闻

URL Source: https://wallstreetcn.com/

Markdown Content:
# 华尔街见闻

*   [首页](https://wallstreetcn.com/)
*   [资讯](https://wallstreetcn.com/news)
*   [快讯](https://wallstreetcn.com/live)
*   [行情](https://wallstreetcn.com/markets)
*   [VIP会员](https://wallstreetcn.com/member/buy/gold)

登录 / 注册

[美元指数 97.93 -0.35 (-0.36%)](https://wallstreetcn.com/markets/codes/DXY.OTC)

[美国4月非农新增就业11.5万人超预期，失业率4.3%](https://wallstreetcn.com/articles/3771861)
[“试图干扰石油出口”，伊朗军方出手！](https://wallstreetcn.com/articles/3771856)
[四部门：探索核电、氢能等能源以直连方式为算力设施供能，持续提升算力设施绿电占比](https://wallstreetcn.com/articles/3771852)

最新资讯

[美国4月非农新增就业11.5万人超预期，失业率4.3%](https://wallstreetcn.com/articles/3771861)

更多消息，持续更新中

葛冬瑾

 2分钟前

[世界杯倒计时！人类：看好法国夺冠，AI：西班牙同样有戏](https://wallstreetcn.com/articles/3771857)

华尔街见闻快讯 21分钟前

[【证监会严肃查处元道通信财务造假案件】近日，证监会对元道通信股份有限公司财务造假案件作出行政处罚事先告知。](https://wallstreetcn.com/livenews/3100705)

华尔街见闻

*   [关于我们](https://wallstreetcn.com/about-us)
"""


WALLSTREETCN_ARTICLE_RAW = """Title: 美国4月非农新增就业11.5万人超预期，失业率4.3%

URL Source: https://wallstreetcn.com/articles/3771861

Published Time: 2026-05-08T12:30:54.000Z

Markdown Content:
# 美国4月非农新增就业11.5万人超预期，失业率4.3% - 华尔街见闻

*   [首页](https://wallstreetcn.com/)
*   [资讯](https://wallstreetcn.com/news)

登录 / 注册

*   2
*   收藏

# 美国4月非农新增就业11.5万人超预期，失业率4.3%

![Image 3: article.author.display_name](https://wpimg-wscn.awtmt.com/478b50b9-9fd3-4275-afc0-f1f5e83cbf37)葛冬瑾 05-08 12:30

更多消息，持续更新中

美国4月非农就业人口增加 11.5万人，预期 6.5万人，前值 17.8万人

美国4月失业率 4.3%，预期 4.3%，前值 4.3%。

更多消息，持续更新中……

风险提示及免责条款

市场有风险，投资需谨慎。本文不构成个人投资建议，也未考虑到个别用户特殊的投资目标、财务状况或需要。用户应考虑本文中的任何意见、观点或结论是否符合其特定状况。据此投资，责任自负。

写评论

最热文章

[霍尔木兹局势又紧张！伊朗称美违反停火空袭、已反击，美军称拦截伊发起的无端袭击](https://wallstreetcn.com/articles/3771778)

华尔街见闻

*   [关于我们](https://wallstreetcn.com/about-us)
"""


MAIMAI_ARTICLE_RAW = """[![](<Base64-Image-Removed>)](https://maimai.cn/ "脉脉")

登录 / 注册

# 背调之前必看，否则offer没了

![](<Base64-Image-Removed>)

宇叔求职陪跑

25-07-31 · HRBP

add-friend好友

💣【TOP8背调翻车原因】

1️⃣ 时间对不上（重灾区！）

"把3个月空窗期合并到上家公司"

👉现在系统自动比对社保/个税 误差超1个月就危险！

2️⃣ 职位/薪资注水

"13k说成15k"

👉银行流水一拉全现形 还会影响定薪！

背调之前必看，否则offer没了脉脉

END

阅读 1

声明：本文内容由脉脉用户自发贡献，部分内容可能整编自互联网。

相关推荐

评论

脉脉App内打开
"""


NOWCODER_DISCUSS_RAW = """# 分享一下秋招开始到现在的面经

精华

10.15号Update

正式结束秋招了

贴了个Offer求比较： [https://www.nowcoder.com/discuss/539985](https://gw-c.nowcoder.com/api/sparta/jump/link?link=https%3A%2F%2Fwww.nowcoder.com%2Fdiscuss%2F539985)

希望大家顺便帮忙看看，老纠结怪了![](https://uploadfiles.nowcoder.com/images/example.png)

到现在为止看了许多牛客的面经，也来回馈一下

语言是C++ 后台方向

# TPLINK一面

1.自我介绍

2.项目相关

3.介绍工厂方法模式

# 阿里云一面

1.上来面试官先自我介绍

2.中断响应的处理过程和机制

[#面经#](https://www.nowcoder.com/creation/subject/demo) [#校招#](https://www.nowcoder.com/creation/subject/demo2)

提示

订阅专刊

点赞成功，聊一聊 >

- 转发到动态

浏览

2.3w

邀请牛友回答

热门话题

#26届春招投递记录#72 讨论

评论
"""


MAIMAI_CLOAK_RAW = """Title: 背调之前必看，否则offer没了

URL Source: https://maimai.cn/article/detail?efid=s09FQ3VV_2bsXT6nprfVew&fid=1882962497

Markdown Content:

登录 / 注册
背调之前必看，否则offer没了
宇叔求职陪跑
25-07-31 · HRBP
好友
💣【TOP8背调翻车原因】

1️⃣ 时间对不上（重灾区！）

"把3个月空窗期合并到上家公司"

END
"""


NOWCODER_CLOAK_RAW = """Title: 分享一下秋招开始到现在的面经

URL Source: https://www.nowcoder.com/discuss/456499

Markdown Content:

首页
题库
面试
登录 / 注册
等了180天终于改名
2021-07-09 17:37
已编辑
字节跳动_抖音_后台开发
关注
分享一下秋招开始到现在的面经
精华
10.15号Update
正式结束秋招了
TPLINK一面

1.自我介绍

2.项目相关

3.介绍工厂方法模式

阿里云一面

1.上来面试官先自我介绍

2.中断响应的处理过程和机制

## 面经##校招##字节跳动
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

    def test_identify_cninfo_as_explicit_platform(self):
        for url in (
            "https://www.cninfo.com.cn/new/commonUrl?url=disclosure/list/notice",
            "https://static.cninfo.com.cn/finalpage/2025-09-05/1224639992.PDF",
        ):
            with self.subTest(url=url):
                platform = identify_platform(url)
                self.assertEqual(platform["id"], "cninfo")
                self.assertEqual(platform["name"], "巨潮资讯")

    def test_identify_sse_as_explicit_platform(self):
        for url in (
            "https://star.sse.com.cn/star/disclosure/listannouncement/",
            "https://big5.sse.com.cn/site/cht/www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2025-10-10/601700_20251010_GVF1.pdf",
        ):
            with self.subTest(url=url):
                platform = identify_platform(url)
                self.assertEqual(platform["id"], "sse")
                self.assertEqual(platform["name"], "上交所")

    def test_identify_reuters_as_explicit_platform(self):
        for url in (
            "https://www.reuters.com/markets/",
            "https://www.reuters.com/business/finance/rbc-lifts-sp-500-year-end-target-7900-ai-optimism-2026-05-08/",
        ):
            with self.subTest(url=url):
                platform = identify_platform(url)
                self.assertEqual(platform["id"], "reuters")
                self.assertEqual(platform["name"], "Reuters")

    def test_identify_hkexnews_as_explicit_platform(self):
        for url in (
            "https://www1.hkexnews.hk/search/titlesearch.xhtml?category=0&lang=EN&market=SEHK&stockId=1000113244",
            "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0408/2026040800057.pdf",
        ):
            with self.subTest(url=url):
                platform = identify_platform(url)
                self.assertEqual(platform["id"], "hkexnews")
                self.assertEqual(platform["name"], "HKEXnews")

    def test_identify_sec_as_explicit_platform(self):
        for url in (
            "https://www.sec.gov/edgar/browse/?CIK=320193&owner=exclude&action=getcompany",
            "https://www.sec.gov/Archives/edgar/data/0000320193/000032019326000013/0000320193-26-000013-index.htm",
        ):
            with self.subTest(url=url):
                platform = identify_platform(url)
                self.assertEqual(platform["id"], "sec")
                self.assertEqual(platform["name"], "SEC EDGAR")

    def test_identify_cls_as_explicit_platform(self):
        for url in (
            "https://www.cls.cn/",
            "https://www.cls.cn/detail/2366149",
        ):
            with self.subTest(url=url):
                platform = identify_platform(url)
                self.assertEqual(platform["id"], "cls")
                self.assertEqual(platform["name"], "财联社")

    def test_identify_eastmoney_as_explicit_platform(self):
        for url in (
            "https://finance.eastmoney.com/",
            "https://finance.eastmoney.com/a/202605073730438926.html",
        ):
            with self.subTest(url=url):
                platform = identify_platform(url)
                self.assertEqual(platform["id"], "eastmoney")
                self.assertEqual(platform["name"], "东方财富")

    def test_identify_sinafinance_as_explicit_platform(self):
        for url in (
            "https://finance.sina.com.cn/",
            "https://finance.sina.com.cn/money/fund/2026-05-08/doc-inhxcusp2275828.shtml",
        ):
            with self.subTest(url=url):
                platform = identify_platform(url)
                self.assertEqual(platform["id"], "sinafinance")
                self.assertEqual(platform["name"], "新浪财经")

    def test_identify_wallstreetcn_as_explicit_platform(self):
        for url in (
            "https://wallstreetcn.com/",
            "https://wallstreetcn.com/articles/3771861",
        ):
            with self.subTest(url=url):
                platform = identify_platform(url)
                self.assertEqual(platform["id"], "wallstreetcn")
                self.assertEqual(platform["name"], "华尔街见闻")

    def test_identify_maimai_as_explicit_platform(self):
        platform = identify_platform("https://maimai.cn/article/detail?efid=s09FQ3VV_2bsXT6nprfVew&fid=1882962497")
        self.assertEqual(platform["id"], "maimai")
        self.assertEqual(platform["name"], "脉脉")
        self.assertEqual(platform["preferred_strategies"][:3], ["firecrawl", "cloakbrowser", "opencli_browser"])

    def test_identify_nowcoder_as_explicit_platform(self):
        platform = identify_platform("https://www.nowcoder.com/discuss/456499")
        self.assertEqual(platform["id"], "nowcoder")
        self.assertEqual(platform["name"], "牛客")
        self.assertEqual(platform["preferred_strategies"][:3], ["firecrawl", "cloakbrowser", "opencli_browser"])

    def test_identify_zhihu_prefers_cloakbrowser_before_opencli(self):
        platform = identify_platform("https://www.zhihu.com/question/10434775822")
        self.assertEqual(platform["id"], "zhihu")
        self.assertEqual(platform["preferred_strategies"][:3], ["firecrawl", "cloakbrowser", "opencli_browser"])


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

    def test_cninfo_pdf_postprocessing_keeps_disclosure_metadata_and_body(self):
        result = postprocess_content(
            CNINFO_PDF_RAW,
            "https://static.cninfo.com.cn/finalpage/2025-09-05/1224639992.PDF",
            {"id": "cninfo", "name": "巨潮资讯", "preferred_strategies": ["jina", "opencli_browser", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# 安徽华恒生物科技股份有限公司第四届董事会第二十三次会议决议公告", result["content"])
        self.assertIn("**证券代码**: 688639", result["content"])
        self.assertIn("**证券简称**: 华恒生物", result["content"])
        self.assertIn("**公告编号**: 2025-034", result["content"])
        self.assertIn("## 正文", result["content"])
        self.assertIn("一、董事会会议召开情况", result["content"])
        self.assertIn("关于公司发行 H 股股票并在香港联合交易所有限公司上市的议案", result["content"])
        self.assertNotIn("本公司董事会及全体董事保证", result["content"])

    def test_cninfo_notice_list_postprocessing_returns_clean_notice_list(self):
        result = postprocess_content(
            CNINFO_LIST_RAW,
            "https://www.cninfo.com.cn/new/commonUrl?url=disclosure/list/notice",
            {"id": "cninfo", "name": "巨潮资讯", "preferred_strategies": ["jina", "opencli_browser", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# 巨潮资讯最新公告", result["content"])
        self.assertIn("## 公告", result["content"])
        self.assertIn("301337 亚华电子", result["content"])
        self.assertIn("关于重大经营合同中标的公告", result["content"])
        self.assertIn("2026-05-08 03:42", result["content"])
        self.assertNotIn("共 768 家 1314 条", result["content"])
        self.assertNotIn("graph_icon", result["content"])

    def test_sse_pdf_postprocessing_keeps_disclosure_metadata_and_body(self):
        result = postprocess_content(
            SSE_PDF_RAW,
            "https://big5.sse.com.cn/site/cht/www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2025-10-10/601700_20251010_GVF1.pdf",
            {"id": "sse", "name": "上交所", "preferred_strategies": ["jina", "opencli_browser", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# 常熟风范电力设备股份有限公司关于以集中竞价方式回购股份的进展公告", result["content"])
        self.assertIn("**证券代码**: 601700", result["content"])
        self.assertIn("**证券简称**: 风范股份", result["content"])
        self.assertIn("**公告编号**: 2025-055", result["content"])
        self.assertIn("## 正文", result["content"])
        self.assertIn("一、回购股份的基本情况", result["content"])
        self.assertIn("二、回购股份的进展情况", result["content"])
        self.assertIn("26,814,100 股", result["content"])
        self.assertNotIn("本公司董事会及全体董事保证", result["content"])

    def test_sse_notice_list_postprocessing_returns_clean_notice_list(self):
        result = postprocess_content(
            SSE_LIST_RAW,
            "https://star.sse.com.cn/star/disclosure/listannouncement/",
            {"id": "sse", "name": "上交所", "preferred_strategies": ["jina", "opencli_browser", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# 上交所公司公告", result["content"])
        self.assertIn("## 公告", result["content"])
        self.assertIn("688001", result["content"])
        self.assertIn("华兴源创", result["content"])
        self.assertIn("2026-05-08", result["content"])
        self.assertIn("股票交易异常波动公告", result["content"])
        self.assertNotIn("上海证券交易所科创板", result["content"])

    def test_reuters_article_postprocessing_keeps_article_body_only(self):
        result = postprocess_content(
            REUTERS_ARTICLE_RAW,
            "https://www.reuters.com/business/finance/rbc-lifts-sp-500-year-end-target-7900-ai-optimism-2026-05-08/",
            {"id": "reuters", "name": "Reuters", "preferred_strategies": ["opencli_browser", "jina", "playwright", "firecrawl"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# RBC lifts S&P 500 year-end target to 7,900 on AI optimism", result["content"])
        self.assertIn("## 正文", result["content"])
        self.assertIn("RBC Capital Markets raised its year-end target", result["content"])
        self.assertIn("The Canadian brokerage's new target implies a 7.7% upside", result["content"])
        self.assertNotIn("Purchase Licensing Rights", result["content"])
        self.assertNotIn("Our Standards", result["content"])
        self.assertNotIn("Read Next", result["content"])
        self.assertNotIn("Advertisement · Scroll to continue", result["content"])

    def test_reuters_markets_postprocessing_returns_clean_news_list(self):
        result = postprocess_content(
            REUTERS_MARKETS_RAW,
            "https://www.reuters.com/markets/",
            {"id": "reuters", "name": "Reuters", "preferred_strategies": ["opencli_browser", "jina", "playwright", "firecrawl"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# Reuters Markets", result["content"])
        self.assertIn("## Lead", result["content"])
        self.assertIn("Morning Bid: Markets cling on as ceasefire is tested", result["content"])
        self.assertIn("## Asian Markets", result["content"])
        self.assertIn("## European Markets", result["content"])
        self.assertIn("## U.S. Markets", result["content"])
        self.assertIn("ECB's Lagarde is sceptical of euro stablecoins", result["content"])
        self.assertIn("RBC lifts S&P 500 year-end target to 7,900 on AI optimism", result["content"])
        self.assertNotIn("Markets Performance", result["content"])
        self.assertNotIn("Official Data Partner", result["content"])
        self.assertNotIn("Notice of Your Privacy Choices", result["content"])

    def test_hkexnews_title_search_postprocessing_returns_clean_notice_list(self):
        result = postprocess_content(
            HKEX_TITLE_SEARCH_RAW,
            "https://www1.hkexnews.hk/search/titlesearch.xhtml?category=0&lang=EN&market=SEHK&stockId=1000113244",
            {"id": "hkexnews", "name": "HKEXnews", "preferred_strategies": ["jina", "opencli_browser", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# HKEXnews 公司披露", result["content"])
        self.assertIn("## 公告", result["content"])
        self.assertIn("09869 | HELENS", result["content"])
        self.assertIn("RETIREMENT OF EXECUTIVE DIRECTOR AND PROPOSED ELECTION OF EXECUTIVE DIRECTOR", result["content"])
        self.assertIn("31/03/2026 21:32", result["content"])
        self.assertIn("Final Results / Dividend or Distribution", result["content"])

    def test_hkexnews_pdf_postprocessing_keeps_disclosure_metadata_and_body(self):
        result = postprocess_content(
            HKEX_PDF_RAW,
            "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0408/2026040800057.pdf",
            {"id": "hkexnews", "name": "HKEXnews", "preferred_strategies": ["jina", "opencli_browser", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# CONNECTED TRANSACTION AND MAJOR TRANSACTION DISPOSAL OF UK POWER NETWORKS AND NOTICE OF SPECIAL GENERAL MEETING", result["content"])
        self.assertIn("**证券代码**: 1038", result["content"])
        self.assertIn("**发布时间**: Tue, 07 Apr 2026 23:00:48 GMT", result["content"])
        self.assertIn("**页数**: 70", result["content"])
        self.assertIn("## 正文", result["content"])
        self.assertIn("The Board announces that the disposal constitutes a connected transaction", result["content"])
        self.assertNotIn("THIS CIRCULAR IS IMPORTANT AND REQUIRES YOUR IMMEDIATE ATTENTION", result["content"])

    def test_sec_browse_postprocessing_returns_clean_filing_list(self):
        result = postprocess_content(
            SEC_BROWSE_RAW,
            "https://www.sec.gov/edgar/browse/?CIK=320193&owner=exclude&action=getcompany",
            {"id": "sec", "name": "SEC EDGAR", "preferred_strategies": ["jina", "opencli_browser", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# SEC EDGAR Filings", result["content"])
        self.assertIn("## Filings", result["content"])
        self.assertIn("10-Q", result["content"])
        self.assertIn("0000320193-26-000013-index.htm", result["content"])
        self.assertIn("2026-05-01", result["content"])
        self.assertIn("Current report", result["content"])

    def test_sec_index_postprocessing_returns_clean_document_table(self):
        result = postprocess_content(
            SEC_INDEX_RAW,
            "https://www.sec.gov/Archives/edgar/data/0000320193/000032019326000013/0000320193-26-000013-index.htm",
            {"id": "sec", "name": "SEC EDGAR", "preferred_strategies": ["jina", "opencli_browser", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# SEC Filing 0000320193-26-000013", result["content"])
        self.assertIn("**Filing Date**: 2026-05-01", result["content"])
        self.assertIn("**Accepted**: 2026-05-01 06:01:00", result["content"])
        self.assertIn("**Period of Report**: 2026-03-28", result["content"])
        self.assertIn("## Documents", result["content"])
        self.assertIn("1 | 10-Q | 10-Q | 999810", result["content"])
        self.assertIn("5 | XBRL TAXONOMY EXTENSION SCHEMA DOCUMENT | EX-101.SCH | 35423", result["content"])

    def test_cls_home_postprocessing_returns_clean_news_stream(self):
        result = postprocess_content(
            CLS_HOME_RAW,
            "https://www.cls.cn/",
            {"id": "cls", "name": "财联社", "preferred_strategies": ["jina", "opencli_browser", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# 财联社要闻", result["content"])
        self.assertIn("## 新闻流", result["content"])
        self.assertIn("【数据看盘】北向资金联手游资抢筹商业航天人气股", result["content"])
        self.assertIn("特朗普称中美元首会谈将按计划举行", result["content"])
        self.assertIn("三部门联合印发《智能体规范应用与创新发展实施意见》", result["content"])
        self.assertIn("财联社5月8日电，据报道，DeepSeek拟募资最高500亿元人民币", result["content"])
        self.assertNotIn("上证指数", result["content"])
        self.assertNotIn("热门板块", result["content"])

    def test_cls_detail_postprocessing_returns_clean_article(self):
        result = postprocess_content(
            CLS_DETAIL_RAW,
            "https://www.cls.cn/detail/2366149",
            {"id": "cls", "name": "财联社", "preferred_strategies": ["jina", "opencli_browser", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# 冲刺7900点！RBC上调标普500年底目标价 看好AI行业前景", result["content"])
        self.assertIn("**发布时间**: 2026-05-08 09:27 星期五", result["content"])
        self.assertIn("**来源**: 财联社 黄君芝", result["content"])
        self.assertIn("## 摘要", result["content"])
        self.assertIn("①加拿大皇家银行资本市场将标普500指数的年底目标价", result["content"])
        self.assertIn("## 正文", result["content"])
        self.assertIn("最新目标价意味着标普500还能较当前水平上涨约7.6%", result["content"])
        self.assertNotIn("我要评论", result["content"])
        self.assertNotIn("关联话题", result["content"])
        self.assertNotIn("15.46W 人关注", result["content"])

    def test_eastmoney_home_postprocessing_returns_clean_news_stream(self):
        result = postprocess_content(
            EASTMONEY_HOME_RAW,
            "https://finance.eastmoney.com/",
            {"id": "eastmoney", "name": "东方财富", "preferred_strategies": ["jina", "opencli_browser", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# 东方财富财经要闻", result["content"])
        self.assertIn("## 新闻流", result["content"])
        self.assertIn("段永平买入泡泡玛特", result["content"])
        self.assertIn("中国长城关联交易骤增", result["content"])
        self.assertIn("DeepSeek拟募资最高500亿元人民币", result["content"])
        self.assertNotIn("上证指数", result["content"])
        self.assertNotIn("全球时间", result["content"])
        self.assertNotIn("热门板块", result["content"])

    def test_eastmoney_article_postprocessing_returns_clean_article(self):
        result = postprocess_content(
            EASTMONEY_ARTICLE_RAW,
            "https://finance.eastmoney.com/a/202605073730438926.html",
            {"id": "eastmoney", "name": "东方财富", "preferred_strategies": ["jina", "opencli_browser", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# 段永平买入泡泡玛特", result["content"])
        self.assertIn("**发布时间**: 2026-05-07 21:32", result["content"])
        self.assertIn("**来源**: 证券时报网", result["content"])
        self.assertIn("## 正文", result["content"])
        self.assertIn("自己买了一些泡泡玛特（09992.HK）", result["content"])
        self.assertNotIn("收藏", result["content"])
        self.assertNotIn("评论", result["content"])
        self.assertNotIn("相关阅读", result["content"])
        self.assertNotIn("网友点击", result["content"])

    def test_sinafinance_home_postprocessing_returns_clean_news_stream(self):
        result = postprocess_content(
            SINAFINANCE_HOME_RAW,
            "https://finance.sina.com.cn/",
            {"id": "sinafinance", "name": "新浪财经", "preferred_strategies": ["jina", "opencli_browser", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# 新浪财经要闻", result["content"])
        self.assertIn("## 新闻流", result["content"])
        self.assertIn("段永平买入泡泡玛特", result["content"])
        self.assertIn("国泰基金投资运作违规被罚", result["content"])
        self.assertIn("美军对伊朗实施定点打击伊朗反击", result["content"])
        self.assertNotIn("上证综指", result["content"])
        self.assertNotIn("热门资讯", result["content"])

    def test_sinafinance_article_postprocessing_returns_clean_article(self):
        result = postprocess_content(
            SINAFINANCE_ARTICLE_RAW,
            "https://finance.sina.com.cn/money/fund/2026-05-08/doc-inhxcusp2275828.shtml",
            {"id": "sinafinance", "name": "新浪财经", "preferred_strategies": ["jina", "opencli_browser", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# 国泰基金：投资运作违规被罚 多只产品大幅跑输基准仍高收费", result["content"])
        self.assertIn("**发布时间**: 2026年05月08日 07:31", result["content"])
        self.assertIn("**来源**: 面包财经", result["content"])
        self.assertIn("## 正文", result["content"])
        self.assertIn("国泰基金因投资运作违规被中国证监会上海监管局采取责令改正的行政监管措施", result["content"])
        self.assertNotIn("新浪财经APP", result["content"])
        self.assertNotIn("责任编辑：123", result["content"])
        self.assertNotIn("热门评论", result["content"])

    def test_wallstreetcn_home_postprocessing_returns_clean_news_stream(self):
        result = postprocess_content(
            WALLSTREETCN_HOME_RAW,
            "https://wallstreetcn.com/",
            {"id": "wallstreetcn", "name": "华尔街见闻", "preferred_strategies": ["jina", "opencli_browser", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# 华尔街见闻要闻", result["content"])
        self.assertIn("## 新闻流", result["content"])
        self.assertIn("美国4月非农新增就业11.5万人超预期，失业率4.3%", result["content"])
        self.assertIn("“试图干扰石油出口”，伊朗军方出手！", result["content"])
        self.assertIn("【证监会严肃查处元道通信财务造假案件】", result["content"])
        self.assertNotIn("美元指数 97.93", result["content"])
        self.assertNotIn("登录 / 注册", result["content"])

    def test_wallstreetcn_article_postprocessing_returns_clean_article(self):
        result = postprocess_content(
            WALLSTREETCN_ARTICLE_RAW,
            "https://wallstreetcn.com/articles/3771861",
            {"id": "wallstreetcn", "name": "华尔街见闻", "preferred_strategies": ["jina", "opencli_browser", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# 美国4月非农新增就业11.5万人超预期，失业率4.3%", result["content"])
        self.assertIn("**发布时间**: 05-08 12:30", result["content"])
        self.assertIn("**来源**: 葛冬瑾", result["content"])
        self.assertIn("## 正文", result["content"])
        self.assertIn("美国4月非农就业人口增加 11.5万人", result["content"])
        self.assertNotIn("风险提示及免责条款", result["content"])
        self.assertNotIn("写评论", result["content"])
        self.assertNotIn("最热文章", result["content"])

    def test_maimai_article_postprocessing_returns_clean_article(self):
        result = postprocess_content(
            MAIMAI_ARTICLE_RAW,
            "https://maimai.cn/article/detail?efid=s09FQ3VV_2bsXT6nprfVew&fid=1882962497",
            {"id": "maimai", "name": "脉脉", "preferred_strategies": ["firecrawl", "opencli_browser", "jina", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# 背调之前必看，否则offer没了", result["content"])
        self.assertIn("**作者**: 宇叔求职陪跑", result["content"])
        self.assertIn("**发布时间**: 25-07-31", result["content"])
        self.assertIn("**身份**: HRBP", result["content"])
        self.assertIn("## 正文", result["content"])
        self.assertIn("💣【TOP8背调翻车原因】", result["content"])
        self.assertIn("银行流水一拉全现形", result["content"])
        self.assertNotIn("登录 / 注册", result["content"])
        self.assertNotIn("add-friend好友", result["content"])
        self.assertNotIn("END", result["content"])
        self.assertNotIn("声明：", result["content"])
        self.assertNotIn("脉脉App内打开", result["content"])

    def test_nowcoder_discuss_postprocessing_returns_clean_main_post(self):
        result = postprocess_content(
            NOWCODER_DISCUSS_RAW,
            "https://www.nowcoder.com/discuss/456499",
            {"id": "nowcoder", "name": "牛客", "preferred_strategies": ["firecrawl", "opencli_browser", "jina", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# 分享一下秋招开始到现在的面经", result["content"])
        self.assertIn("## 正文", result["content"])
        self.assertIn("10.15号Update", result["content"])
        self.assertIn("## TPLINK一面", result["content"])
        self.assertIn("介绍工厂方法模式", result["content"])
        self.assertIn("## 阿里云一面", result["content"])
        self.assertIn("中断响应的处理过程和机制", result["content"])
        self.assertNotIn("精华", result["content"])
        self.assertNotIn("热门话题", result["content"])
        self.assertNotIn("订阅专刊", result["content"])
        self.assertNotIn("点赞成功", result["content"])
        self.assertNotIn("邀请牛友回答", result["content"])
        self.assertNotIn("#26届春招投递记录", result["content"])

    def test_maimai_cloakbrowser_output_keeps_real_title_and_author(self):
        result = postprocess_content(
            MAIMAI_CLOAK_RAW,
            "https://maimai.cn/article/detail?efid=s09FQ3VV_2bsXT6nprfVew&fid=1882962497",
            {"id": "maimai", "name": "脉脉", "preferred_strategies": ["cloakbrowser", "opencli_browser", "jina", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# 背调之前必看，否则offer没了", result["content"])
        self.assertIn("**作者**: 宇叔求职陪跑", result["content"])
        self.assertNotIn("# 登录 / 注册", result["content"])
        self.assertNotIn("**作者**: 背调之前必看，否则offer没了", result["content"])
        self.assertNotIn("好友", result["content"])

    def test_nowcoder_cloakbrowser_output_treats_plaintext_sections_as_headings(self):
        result = postprocess_content(
            NOWCODER_CLOAK_RAW,
            "https://www.nowcoder.com/discuss/456499",
            {"id": "nowcoder", "name": "牛客", "preferred_strategies": ["cloakbrowser", "opencli_browser", "jina", "playwright"]},
        )

        self.assertTrue(result["success"])
        self.assertIn("# 分享一下秋招开始到现在的面经", result["content"])
        self.assertIn("## TPLINK一面", result["content"])
        self.assertIn("## 阿里云一面", result["content"])
        self.assertNotIn("# 首页", result["content"])
        self.assertNotIn("登录 / 注册", result["content"])


if __name__ == "__main__":
    unittest.main()
