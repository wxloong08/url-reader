---
title: "让 Claude Code 的搜索更好用：SearXNG + url-reader 工作流"
date: 2026-05-07
tags: ["engineering", "ai-toolchain"]
---

## 起因

我在 Claude Code 里导入了 DeepSeek V4.0 Pro 来分担一些任务——有些代码生成场景 DS4 比 Sonnet 便宜，效果也够用。但问题来了：**DS4 不支持 Claude Code 内置的 websearch 工具**。

这意味着让 DS4 做技术调研时，它没法自己搜索。解决方法是走 MCP——用 SearXNG 的 `searxng_web_search` 来补上搜索能力。

搜索解决了，但"点开搜索结果看内容"呢？Claude Code MCP 生态里默认用 `web_url_read`，这东西底层走 Jina Reader。用了一段时间，发现三个问题：

1. **中文站经常挂。** 微信公众号、知乎、小红书动不动就返回 HTTP 451，Jina 对这些平台基本不可用。

2. **没有 fallback。** 挂了就挂了，你得手动换工具重试。有一次在 Reddit 上查 Claude Code 的定价讨论，`web_url_read` 直接返回空 HTML，我只能复制链接开浏览器看。

3. **噪音太多。** 偶尔抓成功了，给你的是整页原始内容——导航栏、侧栏推荐、广告、页脚、评论区签名——真正有用的正文不到一半。

所以我写了 url-reader。

## 做了什么

核心想法很简单：**不信任任何单一的网页抓取方式**。给每个 URL 配置一个策略链，从左到右逐个尝试，哪个成功用哪个。

```
Firecrawl API → OpenCLI Browser → Jina Reader → Playwright
```

- **Firecrawl**：AI 抓取 API，有付费额度，直接返回 Markdown，最快但花钱
- **OpenCLI Browser**：复用你本机的终端浏览器渲染页面然后提取正文——这是我后来发现的中文站救星
- **Jina Reader**：免费的 HTTP API，对英文站和海外论坛效果好，但中文站经常 451
- **Playwright**：完整浏览器自动化，兜底，慢但稳

Firecrawl 没配 API Key？跳过。Jina 返回了反爬页面？检测到就降级。OpenCLI 没装？继续往下。

**关键发现**：OpenCLI 在中文内容上的表现远超预期。知乎、Reddit、微博——这些 Jina 几乎必挂的平台——OpenCLI 全部能正常抓取。而且它在终端里跑，不用像 Playwright 那样启动一个完整的 Chromium。

## 不只是抓取

抓回来只是第一步。原始网页里真正有用的内容通常不到一半。我针对不同平台写了一些清洗规则：

| 平台 | 去噪重点 |
|------|----------|
| NodeSeek | 过滤 "BD"、"支持"、"ID + 谢谢老板"、纯表情回复 |
| 知乎 | 去掉关注统计、客户端下载提示、侧栏推荐 |
| 微信公众号 | 去掉 "继续滑动看下一个"、"喜欢此内容的人还喜欢" |
| 京东/淘宝 | 去掉售后保障、购物指南、版权声明、店铺推广 |
| V2EX/HostLoc | 去掉导航栏、Discuz 页脚、积分规则、发帖工具栏 |

去噪的核心逻辑是信息论信号——一条回复如果没有问号、没有 URL、没有技术关键词、没有数字、长度很短，那它大概率是 "学习了" / "厉害" / "前排" 这类低价值回复。

## 效果

拿我们之前碰到的 Reddit 那个帖子举例：

- `web_url_read`：返回空白（Jina 被 Reddit 屏蔽）
- url-reader：Jina 检测到 "You've been blocked" → 自动降级到 OpenCLI → 拿到完整帖子正文 + 20+ 条评论

Token 方面，粗略估算：清洗前一个 50K 字符的论坛帖子，清洗后大约剩 20-25K。这只是粗略数据——我还没做系统的基准测试（下一篇博客补上）。

## 怎么用

在你的 CLAUDE.md 里加一条规则：

```markdown
## Web Search & Scraping
- 搜索用 SearXNG MCP (searxng_web_search)
- 搜索后跟进阅读用 url-reader，不要用 web_url_read
```

然后：

```bash
pip install python-dotenv firecrawl-py  # firecrawl 可选

# 读取
python -m scripts.main <url>

# 读取并保存到本地
python -m scripts.main <url> --save
```

如果你有 Firecrawl API Key，在项目根目录建个 `.env` 文件：

```bash
FIRECRAWL_API_KEY=fc-YOUR_KEY
```

## 不足

说实话，这东西还比较粗糙。你知道的 bug：

- 知乎专栏的清洗偶尔会过度修剪，导致正文太短被判定失败
- Reddit 的清洗走的是通用规则（generic profile），导航栏和推广帖没清干净
- 没有做并发，批量抓取多个 URL 时只能串行
- benchmark 数据还不够系统化——这是我接下来要补的

不过在日常使用中，它已经替我省了很多重复操作。特别是配合 Claude Code 做技术调研时，点开搜索结果不用再担心 "这个链接会不会又是空白"。

代码在 [github.com/wxloong08/url-reader](https://github.com/wxloong08/url-reader)，MIT 协议。
