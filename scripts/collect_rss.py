#!/usr/bin/env python3
import re
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "sources.yaml"
WINDOW = timedelta(hours=24)
TIMEOUT = 20
HEADERS = {"User-Agent": "SemiconductorNewsletterCollector/0.1"}

def utc_now():
    return datetime.now(timezone.utc)

def normalize_url(url):
    if not url:
        return ""
    try:
        p = urlsplit(url.strip())
        if p.scheme.lower() not in ("http", "https") or not p.netloc:
            return ""
        query = [(k, v) for k, v in parse_qsl(p.query)
                 if not k.lower().startswith("utm_")
                 and k.lower() not in ("fbclid", "gclid")]
        return urlunsplit((
            p.scheme.lower(), p.netloc.lower(), p.path or "/",
            urlencode(sorted(query)), ""
        ))
    except ValueError:
        return ""

def normalize_title(title):
    return re.sub(r"\s+", " ", (title or "").strip()).casefold()

def parse_date(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        try:
            dt = parsedate_to_datetime(value.strip())
        except (TypeError, ValueError, OverflowError):
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def field(entry, names):
    for node in entry.iter():
        if node.tag.split("}")[-1].lower() in names and node.text:
            value = " ".join(node.itertext()).strip()
            if value:
                return value
    return ""

def entry_url(entry):
    for node in entry:
        if node.tag.split("}")[-1].lower() == "link":
            href = node.attrib.get("href", "").strip()
            if href:
                return href
            if node.text and node.text.strip():
                return node.text.strip()
    return ""

def extract_entries(data):
    root = ET.fromstring(data)
    nodes = [n for n in root.iter()
             if n.tag.split("}")[-1].lower() in ("item", "entry")]
    return [{
        "title": field(n, {"title"}),
        "url": entry_url(n),
        "date": field(n, {"pubdate", "published", "updated", "date"}),
        "summary": field(n, {"description", "summary", "encoded", "content"}),
    } for n in nodes]

def fetch(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": "SemiconductorNewsletter/0.1"}
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.read()

def load_sources():
    config = yaml.safe_load(CONFIG.read_text())
    return [s for s in config["sources"] if s.get("enabled") is True]

def main():
    run_at = utc_now()
    cutoff = run_at - WINDOW
    sources = load_sources()
    print("Run time UTC:", run_at.isoformat())
    print("Cutoff UTC:", cutoff.isoformat())
    print("Enabled feeds:", len(sources))

    seen = set()
    totals = {"kept": 0, "old": 0, "future": 0,
              "missing_date": 0, "invalid_date": 0, "duplicate": 0}
    failures = 0
    for source in sources:
        print("\nSOURCE:", source["name"])
        try:
            entries = extract_entries(fetch(source["url"]))
            print("FETCH: PASS | Entries:", len(entries))
        except Exception as exc:
            failures += 1
            print("FETCH: FAIL |", type(exc).__name__, str(exc))
            continue
        counts = {"kept": 0}
        for entry in entries:
            raw_date = entry["date"]
            if not raw_date:
                totals["missing_date"] += 1
                continue
            published = parse_date(raw_date)
            if published is None:
                totals["invalid_date"] += 1
                continue
            if published > run_at:
                totals["future"] += 1
                continue
            if published < cutoff:
                totals["old"] += 1
                continue
            key = normalize_url(entry["url"]) or normalize_title(entry["title"])
            if not key or key in seen:
                totals["duplicate"] += 1
                continue
            seen.add(key)
            totals["kept"] += 1
            counts["kept"] += 1
            print("ARTICLE:")
            print("  Source:", source["name"])
            print("  Title:", entry["title"])
            print("  Published UTC:", published.isoformat())
            print("  URL:", entry["url"])
        print("IN WINDOW, UNIQUE:", counts["kept"])
    print("\nTOTALS:", totals)
    print("FEED FAILURES:", failures)
    print("DRY RUN ONLY: no article data written")
    print("RESULT:", "PASS" if not failures else "FAIL")

if __name__ == "__main__":
    main()
