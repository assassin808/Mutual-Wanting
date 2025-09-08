#!/usr/bin/env python3
"""Compute basic integrity stats for raw Reddit dump JSONL files.

For each input file (JSONL; one JSON object per line) this script reports:
 - path
 - n_lines (non-empty)
 - sha256
 - first_created_utc / last_created_utc (if present)
 - first_iso / last_iso

Missing created_utc fields are ignored for min/max calculations.

Usage:
  python pipeline/archive_integrity.py --files data/raw/*.jsonl --out pipeline/integrity_report.json

Note: This does NOT modify data and does not store user identifiers beyond hash summaries.
"""
from __future__ import annotations
import argparse, json, hashlib, pathlib, datetime as dt

def iter_files(patterns):
    for p in patterns:
        path = pathlib.Path(p)
        if path.is_file():
            yield path
        else:
            # simple glob expansion
            for g in path.parent.glob(path.name):
                if g.is_file():
                    yield g

def sha256_file(path: pathlib.Path):
    h = hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--files', nargs='+', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    report = {'files': []}
    for fp in iter_files(args.files):
        n = 0
        first = None
        last = None
        with open(fp,'r',encoding='utf-8', errors='ignore') as f:
            for line in f:
                if not line.strip():
                    continue
                n += 1
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = obj.get('created_utc')
                if isinstance(ts, (int, float)):
                    if first is None or ts < first:
                        first = ts
                    if last is None or ts > last:
                        last = ts
        entry = {
            'path': str(fp),
            'n_lines': n,
            'sha256': sha256_file(fp),
        }
        if first is not None:
            entry['first_created_utc'] = first
            entry['last_created_utc'] = last
            entry['first_iso'] = dt.datetime.utcfromtimestamp(first).isoformat() + 'Z'
            entry['last_iso'] = dt.datetime.utcfromtimestamp(last).isoformat() + 'Z'
        report['files'].append(entry)

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path,'w',encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"Integrity report -> {out_path}")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""Compute basic integrity stats for historical archive JSONL files.

Outputs (per file): line_count, first_ts, last_ts, sha256 (content), empty_lines, malformed_json.

Usage:
  python pipeline/archive_integrity.py --files pipeline/data/gpt4_to_4o_pre.jsonl pipeline/data/gpt4_to_4o_post.jsonl \
     --out pipeline/data/archive_integrity_report.json
"""
from __future__ import annotations
import argparse, json, hashlib, time

def scan(path: str):
    import json as _json
    line_count=0
    empty=0
    malformed=0
    first_ts=None
    last_ts=None
    h=hashlib.sha256()
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            raw=line
            line=line.strip()
            if not line:
                empty+=1
                continue
            line_count+=1
            h.update(raw.encode('utf-8'))
            try:
                obj=_json.loads(line)
            except Exception:
                malformed+=1
                continue
            ts=obj.get('created_utc')
            if isinstance(ts,(int,float)):
                if first_ts is None or ts < first_ts:
                    first_ts=int(ts)
                if last_ts is None or ts > last_ts:
                    last_ts=int(ts)
    return {
        'file': path,
        'line_count': line_count,
        'empty_lines': empty,
        'malformed_json': malformed,
        'first_ts': first_ts,
        'last_ts': last_ts,
        'sha256': h.hexdigest()
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--files', nargs='+', required=True)
    ap.add_argument('--out', required=True)
    args=ap.parse_args()
    report=[scan(p) for p in args.files]
    out={
        'generated_utc': int(time.time()),
        'files': report
    }
    with open(args.out,'w',encoding='utf-8') as f:
        json.dump(out,f,indent=2)
    print(f"Integrity report -> {args.out}")

if __name__=='__main__':
    main()
