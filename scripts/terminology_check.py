#!/usr/bin/env python3
import argparse, json, os, re

PATTERNS = {
    "deprecated_concision_term": r"Concision\s+Re-?prompt\s+Rate|\bCRR\b\s*(\(|:).*concision|concision.*\bCRR\b",
    "preferred_concision_term": r"Concision\s+Prompt\s+Rate|\bCPR\b",
}

EXCLUDES = [
    # Ignore virtualenvs, outputs, lockfiles
    "pipeline/outputs/",
    ".git/",
    ".venv/",
    "node_modules/",
]

TEXT_EXTS = {".md", ".tex", ".txt", ".json", ".yaml", ".yml", ".py", ".sh", ".xml", ".csv", ".tsv"}


def should_skip(path: str) -> bool:
    for ex in EXCLUDES:
        if ex in path:
            return True
    return False


def scan(root: str) -> dict:
    results = {k: {"count": 0, "matches": []} for k in PATTERNS}
    for base, _, files in os.walk(root):
        if should_skip(base + "/"):
            continue
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext and ext not in TEXT_EXTS:
                continue
            p = os.path.join(base, f)
            if should_skip(p):
                continue
            try:
                with open(p, "r", errors="ignore") as fh:
                    text = fh.read()
            except Exception:
                continue
            for key, pat in PATTERNS.items():
                for m in re.finditer(pat, text, flags=re.IGNORECASE):
                    results[key]["count"] += 1
                    # capture short context
                    start = max(0, m.start() - 40)
                    end = min(len(text), m.end() + 40)
                    snippet = text[start:end].replace("\n", " ")
                    results[key]["matches"].append({"file": p, "span": [m.start(), m.end()], "context": snippet})
    return results


def main():
    ap = argparse.ArgumentParser(description="Scan repository for terminology consistency (CPR vs CRR).")
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="pipeline/outputs/terminology_report.json")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    res = scan(args.root)

    summary = {
        "deprecated_concision_term_hits": res["deprecated_concision_term"]["count"],
        "preferred_concision_term_hits": res["preferred_concision_term"]["count"],
        "note": "Any non-zero deprecated_concision_term_hits indicates lingering CRR-for-concision mentions; convert to CPR.",
        "details": res,
    }

    with open(args.out, "w") as fh:
        json.dump(summary, fh, indent=2)

    # Exit code 1 if deprecated terms found (useful for CI), else 0
    if summary["deprecated_concision_term_hits"] > 0:
        exit(1)

if __name__ == "__main__":
    main()
