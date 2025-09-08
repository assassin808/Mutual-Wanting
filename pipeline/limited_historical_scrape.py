#!/usr/bin/env python3
"""Limited Historical Scrape (API‑only, no external dumps)

Purpose:
  Collect the MAXIMUM DISTINCT submissions still reachable via the live Reddit API
  for one or more subreddits WITHOUT relying on Pushshift / external dumps.

Reality Constraints (hard limits you cannot bypass):
  * Each listing (new, top, controversial, etc.) exposes at most ~1000 items.
  * Search does not accept absolute date ranges; you cannot paginate arbitrarily far back.
  * Deleted/removed items reduce the effective <1000 results you see in `new`.
  * This will NOT yield a complete historical window months back—only a union of
    what is still surfaced today via different sorted views.

Strategy Implemented:
  For each subreddit we gather and de‑duplicate IDs from:
    1. new (up to 1000)
    2. top over time_filters: hour, day, week, month, year, all
    3. controversial over same time_filters
    4. (optional) keyword searches (each up to 1000) with sort='new' and sort='relevance'

Output:
  <out_dir>/<subreddit>_aggregate.jsonl  (unique submissions, arbitrary merged order)
  <out_dir>/<subreddit>_summary.json     (counts per view & overall)
  <out_dir>/scrape_manifest.json        (global manifest over all subs)

Usage Example:
  python pipeline/limited_historical_scrape.py \
      --subreddits-file pipeline/subreddits.txt \
      --out-dir pipeline/data/live_scrape \
      --keywords "gpt,openai,persona" --max-per-view 1000

Note:
  Use this ONLY as an interim stop‑gap until you obtain full archive dumps.
  Downstream analysis scripts should treat these outputs as RECENT ONLY.
"""
from __future__ import annotations
import argparse, json, os, sys, time, pathlib, math
from typing import Dict, List, Iterable, Optional

try:
    import praw
except ImportError:  # pragma: no cover
    print("praw not installed. Run: pip install praw", file=sys.stderr)
    sys.exit(1)


TIME_FILTERS = ["hour", "day", "week", "month", "year", "all"]
SORTED_VIEWS = [
    ("top", TIME_FILTERS),
    ("controversial", TIME_FILTERS),
]


def load_subreddits(path: str) -> List[str]:
    subs: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            subs.append(line)
    return subs


def yield_listing(gen, max_items: int) -> Iterable:
    count = 0
    try:
        for item in gen:
            yield item
            count += 1
            if count >= max_items:
                break
    except Exception as e:  # pragma: no cover
        print(f"[warn] listing error: {e}", file=sys.stderr)


def serialize(sub) -> Dict:
    return {
        "id": sub.id,
        "created_utc": getattr(sub, "created_utc", None),
        "score": getattr(sub, "score", None),
        "num_comments": getattr(sub, "num_comments", None),
        "title": getattr(sub, "title", None),
        "selftext": getattr(sub, "selftext", None),
        "subreddit": str(getattr(sub, "subreddit", "")),
        "author": str(getattr(sub, "author", "")),
        "permalink": getattr(sub, "permalink", None),
        "url": getattr(sub, "url", None),
        "is_self": getattr(sub, "is_self", None),
        "over_18": getattr(sub, "over_18", None),
    }


def collect_for_subreddit(reddit, name: str, keywords: List[str], max_per_view: int, sleep: float) -> Dict:
    sub = reddit.subreddit(name)
    id_seen = set()
    rows: List[Dict] = []
    stats: Dict[str, int] = {}

    def add(label: str, items: Iterable):
        added = 0
        for it in items:
            sid = getattr(it, "id", None)
            if not sid or sid in id_seen:
                continue
            id_seen.add(sid)
            rows.append(serialize(it))
            added += 1
        stats[label] = added

    # 1. new
    add("new", yield_listing(sub.new(limit=None), max_per_view))
    time.sleep(sleep)

    # 2. sorted views with time filters
    for view, tfilters in SORTED_VIEWS:
        for tf in tfilters:
            label = f"{view}_{tf}"
            listing = getattr(sub, view)(time_filter=tf, limit=None)
            add(label, yield_listing(listing, max_per_view))
            time.sleep(sleep)

    # 3. optional keyword searches (new & relevance) to snag any stragglers
    for kw in keywords:
        kw = kw.strip()
        if not kw:
            continue
        for sort in ("new", "relevance"):
            label = f"search_{sort}_{kw}".replace(" ", "_")
            try:
                listing = sub.search(kw, sort=sort, limit=None)
                add(label, yield_listing(listing, max_per_view))
            except Exception as e:  # pragma: no cover
                print(f"[warn] search '{kw}' ({sort}) failed: {e}", file=sys.stderr)
            time.sleep(sleep)

    stats["total_unique"] = len(id_seen)
    return {"rows": rows, "stats": stats}


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subreddits-file", required=True, help="Path to file listing subreddits one per line")
    ap.add_argument("--out-dir", required=True, help="Output directory")
    ap.add_argument("--keywords", default="", help="Comma separated keyword queries (optional)")
    ap.add_argument("--max-per-view", type=int, default=1000, help="Cap per listing/view (<=1000 effective)")
    ap.add_argument("--sleep", type=float, default=0.7, help="Sleep seconds between requests (rate limit cushion)")
    ap.add_argument("--dry-run", action="store_true", help="Just print plan, do not fetch")
    return ap.parse_args()


def ensure_env(var: str):
    val = os.getenv(var)
    if not val:
        print(f"Missing required env var: {var}", file=sys.stderr)
        sys.exit(1)
    return val


def main():
    args = parse_args()
    subs = load_subreddits(args.subreddits_file)
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]

    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("[info] Subreddits:", subs)
    print("[info] Keywords:", keywords)
    print("[info] Views: new + top/controversial across", TIME_FILTERS)
    if args.dry_run:
        print("--dry-run set; exiting before fetch.")
        return

    # Environment credentials
    cid = ensure_env("REDDIT_CLIENT_ID")
    cs = ensure_env("REDDIT_CLIENT_SECRET")
    ua = ensure_env("REDDIT_USER_AGENT")

    reddit = praw.Reddit(client_id=cid, client_secret=cs, user_agent=ua, check_for_async=False)

    manifest = {"subreddits": {}, "keywords": keywords, "max_per_view": args.max_per_view}
    for s in subs:
        print(f"[sub:{s}] collecting ...")
        t0 = time.time()
        result = collect_for_subreddit(reddit, s, keywords, args.max_per_view, args.sleep)
        rows = result["rows"]
        stats = result["stats"]
        # Write rows
        out_rows_path = out_dir / f"{s}_aggregate.jsonl"
        with out_rows_path.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        # Write stats
        stats_path = out_dir / f"{s}_summary.json"
        with stats_path.open("w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
        dt = time.time() - t0
        print(f"[sub:{s}] unique={stats['total_unique']} views={len(stats)-1} time={dt:.1f}s -> {out_rows_path}")
        manifest["subreddits"][s] = {"unique": stats["total_unique"], "stats": stats}

    with (out_dir / "scrape_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print("[done] Manifest written.")


if __name__ == "__main__":  # pragma: no cover
    main()
