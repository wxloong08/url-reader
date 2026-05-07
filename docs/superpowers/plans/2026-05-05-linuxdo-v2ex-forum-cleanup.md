# Linux.do And V2EX Forum Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add explicit `LINUX DO` and `V2EX` topic cleanup, and fix false-positive platform detection for `v2ex.com`.

**Architecture:** Keep platform recognition in `scripts/platforms.py`, add topic-specific extraction in `scripts/content.py`, and lock behavior with small raw-fixture tests in `tests/test_content.py`.

**Tech Stack:** Python, unittest, existing Jina-based scraping pipeline

---

### Task 1: Lock the broken behavior with tests

**Files:**
- Modify: `tests/test_content.py`
- Test: `tests/test_content.py`

- [ ] Add tests for `linux.do` and `v2ex.com` platform identification.
- [ ] Add a regression test proving `https://www.v2ex.com/` is not identified as `X`.
- [ ] Add raw-fixture tests for `LINUX DO` topic extraction.
- [ ] Add raw-fixture tests for `V2EX` topic extraction and reply filtering.
- [ ] Run: `python -m unittest tests.test_content -v`
- [ ] Confirm the new tests fail before implementation.

### Task 2: Implement explicit platform support

**Files:**
- Modify: `scripts/platforms.py`

- [ ] Replace substring domain checks with exact-or-subdomain matching.
- [ ] Add explicit `linuxdo` and `v2ex` platform definitions.
- [ ] Re-run: `python -m unittest tests.test_content -v`
- [ ] Confirm identification tests pass or move remaining failures into extractor work.

### Task 3: Implement topic extractors

**Files:**
- Modify: `scripts/content.py`
- Test: `tests/test_content.py`

- [ ] Add `linuxdo` and `v2ex` to forum-platform routing.
- [ ] Implement a `linux.do` topic extractor.
- [ ] Implement a `V2EX` topic extractor.
- [ ] Reuse existing low-information reply filtering where appropriate.
- [ ] Run: `python -m unittest tests.test_content tests.test_formatter`
- [ ] Confirm all tests pass.

### Task 4: Verify on real URLs

**Files:**
- Modify: none

- [ ] Run: `python -m scripts.main "https://linux.do/t/topic/2115948"`
- [ ] Run: `python -m scripts.main "https://www.v2ex.com/t/1210308"`
- [ ] Confirm both outputs show clean thread bodies and filtered replies.
