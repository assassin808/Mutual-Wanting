#!/usr/bin/env python3
"""CLI annotation tool for pilot submissions aligned with updated labeling_guidelines.md.

Primary tags: WARMTH_LOSS, CREATIVITY_DROP, HELPFULNESS_REGRESSION, HEDGING_SHIFT,
SAFETY_REFUSAL_SHIFT, MEMORY_CONTINUITY, VERBOSITY_CHANGE, LATENCY_SPEED,
ACCESS_LIMITS, UPGRADE_BENEFIT, NONE

Secondary flags: ANTHRO_LANG, PARASOCIAL, NOSTALGIA, POSITIVE_COUNTER, META_SPECULATION
"""
from __future__ import annotations
import csv, argparse, random, json, time
from typing import List, Dict, Optional

PRIMARY_TAGS = [
    'WARMTH_LOSS','CREATIVITY_DROP','HELPFULNESS_REGRESSION','HEDGING_SHIFT',
    'SAFETY_REFUSAL_SHIFT','MEMORY_CONTINUITY','VERBOSITY_CHANGE','LATENCY_SPEED',
    'ACCESS_LIMITS','UPGRADE_BENEFIT','NONE'
]
SECONDARY_FLAGS = ['ANTHRO_LANG','PARASOCIAL','NOSTALGIA','POSITIVE_COUNTER','META_SPECULATION']

def load_rows(path: str) -> List[Dict[str,str]]:
    with open(path,'r',encoding='utf-8') as f:
        return list(csv.DictReader(f))

def save_rows(path: str, rows: List[Dict[str,str]], fieldnames):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def wrap(text: str, width: int=110) -> str:
    out=[]; line=''
    for tok in text.split():
        if len(line)+1+len(tok) > width:
            out.append(line); line=tok
        else:
            line = tok if not line else line+' '+tok
    if line: out.append(line)
    return '\n'.join(out)

def menu():
    print('Primary Tags:')
    for i,t in enumerate(PRIMARY_TAGS, start=1):
        print(f'  {i}. {t}')
    print('Secondary Flags:')
    for i,f in enumerate(SECONDARY_FLAGS, start=1):
        print(f'  [{i}] {f}')

def emit_progress(rows: List[Dict[str,str]], annotator: str, path: Optional[str]):
    if not path: return
    total = len(rows)
    labeled = sum(1 for r in rows if r.get('primary_tag'))
    dist = {}
    for r in rows:
        tag = r.get('primary_tag')
        if tag:
            dist[tag] = dist.get(tag,0)+1
    payload = {
        'timestamp': time.time(),
        'annotator': annotator,
        'total': total,
        'labeled': labeled,
        'pct_labeled': labeled/total if total else 0,
        'label_dist': dist
    }
    with open(path,'w',encoding='utf-8') as f:
        json.dump(payload,f,indent=2)

def annotate(rows: List[Dict[str,str]], annotator: str, out_path: str, autosave: int, progress_path: Optional[str]):
    fieldnames = rows[0].keys()
    updated=0
    total = len(rows)
    for idx,row in enumerate(rows):
        if row.get('primary_tag'):
            continue
        remaining = sum(1 for r in rows if not r.get('primary_tag'))
        text = (row.get('title','') + '\n' + (row.get('selftext','') or '')).strip()
        print(f"\n=== Item {idx} / {total-1} (remaining unlabeled: {remaining}) ID={row.get('id','')} ===")
        print(wrap(text[:1500]))
        menu()
        while True:
            sel = input('Select # | f=flags | n=skip | q=quit: ').strip()
            if sel=='q':
                save_rows(out_path, rows, fieldnames)
                emit_progress(rows, annotator, progress_path)
                print('Progress saved. Exiting.')
                return updated
            if sel=='n':
                break
            if sel=='f':
                raw = input('Flag indices (comma): ').strip()
                chosen=[]
                for part in raw.split(','):
                    part=part.strip()
                    if part.isdigit():
                        i=int(part)
                        if 1<=i<=len(SECONDARY_FLAGS):
                            chosen.append(SECONDARY_FLAGS[i-1])
                row['secondary_flags']=';'.join(chosen)
                continue
            if sel.isdigit():
                num=int(sel)
                if 1<=num<=len(PRIMARY_TAGS):
                    row['primary_tag']=PRIMARY_TAGS[num-1]
                    row['annotator_id']=annotator
                    updated+=1
                    break
            print('Invalid input.')
        if autosave and updated and updated % autosave == 0:
            save_rows(out_path, rows, fieldnames)
            emit_progress(rows, annotator, progress_path)
            print(f'(autosaved {updated})')
    save_rows(out_path, rows, fieldnames)
    emit_progress(rows, annotator, progress_path)
    print('All items processed.')
    return updated

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--annotator', required=True)
    ap.add_argument('--shuffle', action='store_true', help='Shuffle item order (recommended to reduce order bias)')
    ap.add_argument('--autosave', type=int, default=5, help='Autosave interval (labeled items)')
    ap.add_argument('--progress_out', help='Write rolling progress JSON here')
    args = ap.parse_args()
    rows = load_rows(args.inp)
    if args.shuffle:
        random.seed(42)
        random.shuffle(rows)
    n = annotate(rows, args.annotator, args.out, args.autosave, args.progress_out)
    print(f'Annotated {n} rows.')

if __name__ == '__main__':
    main()
