# Linux.do And V2EX Forum Cleanup Design

**Goal**

Add explicit support for `linux.do` and `v2ex.com` topic pages so saved Markdown is research-friendly instead of generic page dumps.

**Scope**

- Add explicit platform identification for `linux.do` and `v2ex.com`.
- Fix domain matching so `v2ex.com` is not misidentified as `X`.
- Add topic extractors for `LINUX DO` and `V2EX`.
- Reuse the existing low-information reply filter for forum replies.
- Add regression tests for identification and content extraction.

**Non-Goals**

- Cleaning list pages or homepages into summaries.
- Ranking replies by quality beyond the current conservative reply filter.
- Adding article-site support for `36Kr`, `少数派`, or `CSDN` in this round.

## Current Problems

1. `identify_platform()` uses substring matching, so `www.v2ex.com` incorrectly matches `x.com`.
2. `linux.do` topic pages are not recognized as forums and fall back to generic cleanup.
3. `V2EX` topic pages have a custom structure with promoted blocks, breadcrumbs, topic metadata, and reply formatting that generic cleanup does not handle well.

## Design

### Platform Identification

- Replace substring domain matching with exact-or-subdomain matching.
- Add:
  - `linuxdo` → `linux.do`
  - `v2ex` → `v2ex.com`, `www.v2ex.com`

### Linux.do Extraction

Treat `linux.do` as a Discourse-style topic page:

- Use the metadata title as the thread title.
- Ignore navigation, categories, tags, and community banner content before the first `## post by ...` marker.
- Parse the first post as the main thread body.
- Parse subsequent `## post by ...` blocks as replies.
- Stop at `### Related topics`.
- Drop avatar-only lines, solution label noise, and low-information replies.

Output shape:

```md
# Title
**楼主**: ...
**发布时间**: ...

## 主楼
...

## 回复
1. user | time
...
```

### V2EX Extraction

Treat `V2EX` as a topic page with one main post and a flat reply list:

- Start from the actual topic title block, not the promoted block above it.
- Capture the first member link as the author.
- Keep the main post until the `replies` marker.
- Parse replies from the repeated avatar/member/time blocks.
- Stop before footer sections such as `通过 Atom Feed 订阅`, `More Recent Topics`, and site-wide curated nodes.
- Reuse conservative low-information reply filtering.

## Testing

- Add failing tests for:
  - `linux.do` platform identification
  - `v2ex.com` platform identification
  - `v2ex.com` not misidentified as `X`
  - `linux.do` topic extraction
  - `V2EX` topic extraction
- Verify with real `python -m scripts.main <url>` runs against one public topic from each site.
