import json
import sys
from datetime import timedelta
from pathlib import Path

import collect_rss as rss
from relevance import assess_relevance
from scoring import score_article
from interpretation import interpret_article
from render_newsletter import render_newsletter

ROOT = Path(__file__).resolve().parent.parent


def main():
    now = rss.utc_now()
    cutoff = now - timedelta(hours=24)
    seen = set()
    articles = []
    failures = 0
    ai_attempted = 0
    ai_succeeded = 0

    for source in rss.load_sources():
        try:
            entries = rss.extract_entries(rss.fetch(source["url"]))
        except Exception as exc:
            print("FEED FAIL:", source["name"], str(exc))
            failures += 1
            continue

        for entry in entries:
            published = rss.parse_date(entry.get("date"))
            if not published or not cutoff <= published <= now:
                continue

            title = entry.get("title", "").strip()
            url = entry.get("url", "")
            key = rss.normalize_url(url) or rss.normalize_title(title)

            if not title or not url or not key or key in seen:
                continue
            seen.add(key)

            article = {
                "title": title,
                "url": url,
                "source": source["name"],
                "source_id": source["id"],
                "summary": entry.get("summary", ""),
                "published_at": published.isoformat(),
            }

            if source["id"] == "businesstimes_companies_markets":
                import re
                text = article["title"] + " " + article["summary"]
                topics = r"\b(AI|artificial intelligence|machine learning|data cent(er|re)s?|GPU|semiconductor|chipmaker|chip design|chip manufacturing|foundry|wafer|HBM|DRAM|NAND|AI chip|AI server|AI infrastructure)\b"
                if not re.search(topics, text, re.I):
                    continue
                relevance = {"eligible": True, "relevance_score": 3}
            else:
                relevance = assess_relevance(
                    article["title"], article["summary"]
                )
            if not relevance["eligible"]:
                continue

            article["relevance_score"] = relevance["relevance_score"]
            article["interpretation"] = None

            if __import__("os").getenv("DEEPSEEK_API_KEY"):
                ai_attempted += 1
                try:
                    article["interpretation"] = interpret_article(article)
                    ai_succeeded += 1
                except Exception as exc:
                    print("AI FAIL:", title, str(exc))

            article["interpretation_valid"] = bool(
                article["interpretation"]
            )
            article["final_score"] = score_article(article)
            articles.append(article)

    articles.sort(
        key=lambda a: (a["final_score"], a["published_at"]),
        reverse=True,
    )
    selected = articles[:12]

    data = {
        "generated_at": now.isoformat(),
        "mode": ("LOCAL PREVIEW — AI NOT RUN" if not __import__("os").getenv("DEEPSEEK_API_KEY") else "AI — FAIL" if ai_succeeded == 0 else "AI — PARTIAL" if ai_succeeded < ai_attempted else "AI — PASS"),
        "ai_attempted": ai_attempted,
        "ai_succeeded": ai_succeeded,
        "feed_failures": failures,
        "eligible_count": len(articles),
        "selected_count": len(selected),
        "articles": selected,
    }

    (ROOT / "runtime/newsletter.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    )
    (ROOT / "docs/index.html").write_text(
        render_newsletter(
            selected, now.isoformat(),
            preview=True,
        ),
        encoding="utf-8",
    )

    print("Eligible:", len(articles))
    print("Selected:", len(selected))
    print("Feed failures:", failures)
    print("JSON: runtime/newsletter.json")
    print("HTML: docs/index.html")
    print("RESULT:", "PASS" if failures == 0 else "PASS WITH WARNINGS")


if __name__ == "__main__":
    main()
