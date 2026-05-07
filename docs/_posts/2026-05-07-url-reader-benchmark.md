---
layout: post
title: "url-reader Benchmark：跨平台网页抓取成功率与 Token 压缩率实测"
date: 2026-05-07
categories: [engineering, benchmark]
---

## 为什么做这个基准测试

url-reader 是一个多策略网页抓取工具，覆盖 20+ 平台，支持 4 种抓取策略的自动降级。但数据说话——本文用真实 URL 做横向对比，测量三个指标：

1. **成功率**：不同平台下策略链能否拿到有效内容
2. **策略命中率**：哪个策略实际完成抓取
3. **Token 压缩率**：清洗后减少了多少无用 token

## 测试环境

- Firecrawl API Key：已配置
- OpenCLI：`opencli.cmd` v0.0.0
- Jina Reader：`r.jina.ai`（免费层）
- Playwright：Chromium headless

## 方法

每个 URL 依次尝试平台的策略链，首个成功则停止。记录：

```
平台 → 命中策略 → 原始字符数 → 清洗后字符数 → 清洗 profile
```

6 个平台 × 3 种内容类型（问答/论坛/博客）：

| 平台 | URL | 类型 |
|------|-----|------|
| 知乎 | /question/10434775822 | Q&A |
| Reddit | /r/ClaudeAI/comments/1qfosa6 | 论坛 |
| SSDNodes | /blog/claude-code-pricing... | 技术博客 |
| V2EX | /t/1035000 | 论坛 |
| NodeSeek | /post-260001-1 | 论坛 |
| 知乎专栏 | /p/2012957546835625895 | 文章 |

## 结果

### 成功率：5/6（83%）

| 平台 | 命中策略 | 耗时 | 字符压缩率 |
|------|----------|------|-----------|
| 知乎问答 | OpenCLI Browser | 11.4s | 42% |
| Reddit | OpenCLI Browser | 13.7s | 38% |
| SSDNodes 博客 | Firecrawl | 1.3s | 7%† |
| V2EX | Jina Reader | 3.2s | 45% |
| NodeSeek | Jina Reader | 2.6s | 52% |
| 知乎专栏 | **失败** | - | - |

† Firecrawl 返回的已是干净 Markdown，清洗空间小。Jina 和 OpenCLI 返回的含大量导航噪音，去噪效果明显。

### 策略命中分布

```
OpenCLI Browser  ████████ 2 (知乎, Reddit)
Jina Reader      ████████ 2 (V2EX, NodeSeek)
Firecrawl        ████     1 (SSDNodes)
Playwright       ░░░░     0 (未触发)
```

关键发现：**没有任何单一策略能覆盖全部平台。** 这正是多策略链的价值——OpenCLI 打中国社交平台，Jina 打技术论坛，Firecrawl 打标准博客。

### Token 压缩效果

30-50% 的字符压缩率在 LLM 上下文中意味着：

| 场景 | 原始 token* | 清洗后 token* | 节省 |
|------|------------|-------------|------|
| 知乎问答 | ~6,000 | ~3,500 | 42% |
| Reddit 帖子+回复 | ~4,000 | ~2,500 | 38% |
| NodeSeek 帖子 | ~12,000 | ~5,800 | 52% |
| V2EX 帖子 | ~5,000 | ~2,800 | 45% |

*估算：4 字符/token

## 为什么知乎专栏失败

Firecrawl 对知乎专栏 URL 返回了验证码页面（"环境异常，需要验证"）。这是 Firecrawl 的已知限制——对需要登录或反爬严格的中国平台，API 方式容易触发风控。此时 OpenCLI Browser 应该是后续策略，但当前知乎专栏走的是 `article_feed` 而非 `qa_answers` 清洗模式，策略链为 `Firecrawl → OpenCLI → Jina → Playwright`，理论上应该降级成功。实际测试中降级到了 OpenCLI 但清洗后内容过短被判定失败。（此问题已在 v2.0.1 修复。）

## 方法论反思

1. **单一策略不可靠**：任何抓取方式都有盲区。Firecrawl 怕验证码，Jina 怕 Reddit/知乎，OpenCLI 对纯 JS 渲染页面有限制。
2. **内容清洗 ≠ 压缩**：真正的价值不是把内容变短，而是把噪音去掉——让 LLM 更快地定位到关键信息。
3. **Firecrawl 最快但最贵**：1.3s vs OpenCLI 的 10-15s。如果量大且付费，Firecrawl 最优；日常使用，OpenCLI + Jina 免费链足够。

## 开源

url-reader v2.0.0 开源在 [github.com/wxloong08/url-reader](https://github.com/wxloong08/url-reader)，MIT License。
