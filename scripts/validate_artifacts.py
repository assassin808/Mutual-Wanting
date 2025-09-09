#!/usr/bin/env python3
"""
Validate JSON/CSV artifacts in a directory: ensure loadable JSON, non-empty CSVs.
Outputs a JSON summary with file statuses.
"""
import argparse, os, json
import csv


def validate_dir(path: str):
    result = {"dir": path, "files": []}
    for root, _, files in os.walk(path):
        for fn in files:
            fp = os.path.join(root, fn)
            status = {"path": fp, "ok": True, "type": None, "note": ""}
            try:
                if fn.endswith('.json'):
                    status["type"] = "json"
                    with open(fp, 'r', encoding='utf-8') as f:
                        json.load(f)
                elif fn.endswith('.csv') or fn.endswith('.tsv'):
                    status["type"] = "csv"
                    with open(fp, 'r', encoding='utf-8') as f:
                        dialect = csv.excel_tab if fn.endswith('.tsv') else csv.excel
                        rdr = csv.reader(f, dialect=dialect)
                        first = next(rdr, None)
                        if first is None:
                            status["ok"] = False
                            status["note"] = "empty file"
                else:
                    status["type"] = "other"
            except Exception as e:
                status["ok"] = False
                status["note"] = str(e)
            result["files"].append(status)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    out = validate_dir(args.dir)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2)
    print(f"Artifact validation -> {args.out}")


if __name__ == '__main__':
    main()
