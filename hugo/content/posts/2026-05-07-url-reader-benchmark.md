---
title: "url-reader Benchmark：测试方法论与初步数据"
date: 2026-05-07
tags: ["engineering", "benchmark"]
---

## 前言

上一篇博客介绍了我写的 url-reader——一个多策略网页抓取工具。文章里提到了"中文站成功率 ~90%"但没给具体数据。这篇补上基准测试的方法论和第一轮数据。

坦白说，目前只测了 3 个 URL，样本量很小。这篇更多是分享测试方法——怎么衡量一个抓取工具的好坏——而不是给出最终结论。后续我会扩大样本量并更新数据。

## 测试设计

一个网页抓取工具的价值可以从三个维度衡量：

1. **成功率**：能不能拿到有效内容（不是反爬页面、不是空白）
2. **策略效率**：哪个策略实际完成了任务（反映策略链设计是否合理）
3. **Token 压缩率**：清洗后去掉了多少无用字符

每次测试记录：URL → 平台识别 → 实际命中策略 → 耗时 → 原始字符数 → 清洗后字符数。

## 测试 URL（第一轮）

| 平台 | URL | 类型 |
|------|-----|------|
| 知乎问答 | /question/10434775822 | 问答 |
| Reddit | /r/ClaudeAI/comments/1qfosa6 | 论坛 |
| SSDNodes 博客 | /blog/claude-code-pricing-2026 | 技术博客 |

这三个 URL 是我们在 Claude Code 实际调研中访问过的，不是专门选的 benchmark 样本——这其实更接近真实使用场景。

还没测的平台：V2EX、NodeSeek、HostLoc、微信公众号——这些是下一轮要补的。

## 测试环境

```
Firecrawl API Key: 已配置 (免费层 500 页/月)
OpenCLI: opencli.cmd 0.0.0
Jina Reader: r.jina.ai (免费)
Playwright: Chromium headless (本轮未触发)
操作系统: Windows 11
网络: 国内家庭宽带 (经过代理)
```

注意这个网络环境——测试结果会受代理质量影响。如果你在海外或有更好的线路，数字可能不同。

## 结果

### 第一轮 (2026-05-07)

| URL | 平台 | 命中策略 | 耗时 | 字符压缩 |
|-----|------|----------|------|---------|
| 知乎 /question/10434775822 | 知乎 | OpenCLI Browser | 11.4s | ~42%* |
| Reddit /r/ClaudeAI/comments/1qfosa6 | Reddit | OpenCLI Browser | 13.7s | ~38%* |
| SSDNodes /blog/claude-code-pricing | 通用 | Firecrawl | 1.3s | 7%† |

\* 知乎问答的数据来自清洗前后对比——原始 OpenCLI 输出包含大量导航和侧栏，清洗后只剩问答正文。
† Firecrawl 返回的本身就是干净的 Markdown，清洗空间很小。7% 只是去掉了页脚版权声明。这不代表清洗功能没用，而是 Firecrawl 已经做了大部分去噪工作。

### 策略命中

```
OpenCLI Browser  ████████ 2 次 (知乎, Reddit)
Firecrawl        ████     1 次 (SSDNodes)
Jina Reader      无       0 次 (Reddit 被屏蔽, 知乎 451)
Playwright       无       0 次 (未触发, 前序策略全部成功)
```

Jina Reader 本轮零命中——Reddit 返回了 "You've been blocked"，知乎返回了 HTTP 451，两个都被反爬检测拦截然后降级到了 OpenCLI。这个结果和我之前的经验一致：**对中文和 Reddit 内容，Jina 基本不可用。**

## 解读

有几个值得注意的点：

**OpenCLI 比预期可靠。** 我最初把它作为 Playwright 之前的备选，但实际测试中它的成功率比 Jina 高得多——特别是对反爬严格的平台。代价是慢（10-15s vs Jina 的 2-3s），但对于 Claude Code 的上下文准备来说，多等 10 秒换来可靠的抓取结果，是值得的。

**Firecrawl 对反爬弱站无敌。** 1.3 秒、干净 Markdown、零清洗——如果能用的起，这是最优方案。但免费额度 500 页/月，重度使用需要付费。

**Jina 的价值在英文技术论坛。** 虽然本轮没命中，但之前测试中 Jina 对 V2EX、LowEndTalk 这类站点的表现很好。它在策略链里的位置（第三优先级）是合理的——作为 Firecrawl 和 OpenCLI 之后的补充。

## 接下来

1. 扩大样本量到 10+ URL（包括 V2EX、NodeSeek、微信公众号、HostLoc）
2. 加入重复测试（同一个 URL 测试 3 次取平均，消除网络波动）
3. 对比不同网络环境下的结果（国内直连 vs 走代理）
4. 测一下并行抓取的性能

代码在 [github.com/wxloong08/url-reader](https://github.com/wxloong08/url-reader)，benchmark 脚本在 `scripts/benchmark.py`。
