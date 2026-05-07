"""url-reader benchmark — measure success rate and token reduction across platforms."""

import json
import time
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
from scripts.main import read_url

BENCHMARK_URLS = [
    # (platform, url, expected_type)
    ("知乎问答", "https://www.zhihu.com/question/10434775822", "qa"),
    ("Reddit", "https://www.reddit.com/r/ClaudeAI/comments/1qfosa6/", "forum"),
    ("技术博客(GitHub Pages)", "https://www.ssdnodes.com/blog/claude-code-pricing-in-2026-every-plan-explained-pro-max-api-teams/", "blog"),
]

def count_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for mixed CN/EN text."""
    return max(1, len(text) // 4)


def run_benchmark():
    results = []
    for name, url, _url_type in BENCHMARK_URLS:
        print(f"\n{'='*60}")
        print(f"Benchmark: {name}")
        print(f"URL: {url}")
        start = time.time()
        result = read_url(url, verbose=False)
        elapsed = time.time() - start

        entry = {
            "platform": name,
            "url": url,
            "strategy": result.get("strategy", "unknown"),
            "success": result.get("success", False),
            "time_seconds": round(elapsed, 1),
        }

        if result.get("success"):
            metadata = result.get("metadata", {})
            raw_chars = metadata.get("cleanup_chars_before", 0)
            clean_chars = metadata.get("cleanup_chars_after", 0)
            entry["raw_chars"] = raw_chars
            entry["clean_chars"] = clean_chars
            entry["raw_tokens_est"] = count_tokens("x" * raw_chars) if raw_chars else 0
            entry["clean_tokens_est"] = count_tokens("x" * clean_chars) if clean_chars else 0
            entry["char_reduction"] = f"{(1 - clean_chars/max(raw_chars,1))*100:.0f}%"
            entry["cleanup_profile"] = metadata.get("cleanup_profile", "none")
        else:
            entry["error"] = "; ".join(result.get("errors", ["unknown"]))

        results.append(entry)
        status = "OK" if entry["success"] else "FAIL"
        strategy = entry.get("strategy", "N/A")
        reduction = entry.get("char_reduction", "N/A")
        print(f"  [{status}] strategy={strategy} time={elapsed:.1f}s reduction={reduction}")

    # Summary
    success_count = sum(1 for r in results if r["success"])
    total = len(results)
    print(f"\n{'='*60}")
    print(f"Summary: {success_count}/{total} successful")
    print(f"Strategies used: {set(r['strategy'] for r in results if r['success'])}")

    # Save
    output_path = Path(__file__).parent.parent / "benchmark_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Results saved to {output_path}")

    return results


if __name__ == "__main__":
    run_benchmark()
