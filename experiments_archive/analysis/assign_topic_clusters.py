#!/usr/bin/env python3
"""Assign topic clusters to normalized pre/post corpora for a transition.

Method:
  - Load normalized pre + post JSONL.
  - Extract text (body) with fallback to title if body empty and title present (future improvement: incorporate title field earlier in normalization pipeline).
  - TF-IDF (unigrams + bigrams, min_df=3) -> KMeans (k provided or heuristic sqrt(N/2) clipped).
  - Write cluster assignments back out to a cluster mapping CSV and enriched sampling frame (replacing cluster_id=-1).

Outputs:
  pipeline/outputs/annotation/{transition}_clusters.csv
  pipeline/outputs/annotation/{transition}_sampling_frame_clusters.csv

Note: Does not overwrite original sampling frame; produces a new file with cluster ids.
"""
from __future__ import annotations
import argparse, json, os, csv, math
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


def load_rows(path: str) -> List[Dict[str,Any]]:
    rows=[]
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line: continue
            try:
                rows.append(json.loads(line))
            except:  # noqa
                continue
    return rows


def build_text(r: Dict[str,Any]) -> str:
    body = (r.get('body') or '').strip()
    title = (r.get('title') or '').strip()
    if body:
        return body
    return title


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--transition-id', required=True)
    ap.add_argument('--k', type=int, help='Number of clusters (if omitted heuristic)')
    ap.add_argument('--data-dir', default='pipeline/data')
    ap.add_argument('--out-dir', default='pipeline/outputs/annotation')
    args=ap.parse_args()

    pre=os.path.join(args.data_dir,f"{args.transition_id}_pre.jsonl")
    post=os.path.join(args.data_dir,f"{args.transition_id}_post.jsonl")
    if not (os.path.exists(pre) and os.path.exists(post)):
        raise SystemExit('Normalized corpora not found')

    pre_rows=load_rows(pre)
    post_rows=load_rows(post)
    all_rows=pre_rows+post_rows
    texts=[build_text(r) for r in all_rows]
    # Filter out empty texts
    non_empty=[(i,t) for i,t in enumerate(texts) if t]
    if not non_empty:
        raise SystemExit('No non-empty texts to cluster')

    idxs, corpus = zip(*non_empty)
    k = args.k or max(2, min(20, int(round(math.sqrt(len(corpus)/2)))))

    vec=TfidfVectorizer(ngram_range=(1,2), min_df=3, max_features=5000)
    X=vec.fit_transform(corpus)
    km=KMeans(n_clusters=k, n_init='auto', random_state=42)
    labels=km.fit_predict(X)

    # Prepare mapping
    os.makedirs(args.out_dir, exist_ok=True)
    cluster_csv=os.path.join(args.out_dir,f"{args.transition_id}_clusters.csv")
    with open(cluster_csv,'w',newline='',encoding='utf-8') as f:
        w=csv.writer(f)
        w.writerow(['row_index','cluster','pre_post','score_bucket'])
        for seq,(row_i,lbl) in enumerate(zip(idxs, labels)):
            phase=all_rows[row_i].get('pre_post')
            sb=all_rows[row_i].get('score_bucket')
            w.writerow([row_i,lbl,phase,sb])

    # Build enriched sampling frame
    enriched_path=os.path.join(args.out_dir,f"{args.transition_id}_sampling_frame_clusters.csv")
    with open(enriched_path,'w',newline='',encoding='utf-8') as f:
        w=csv.writer(f)
        header=['id','transition','pre_post','subreddit','score_bucket','length_bucket','question_flag','sentiment','cluster_id','token_len']
        w.writerow(header)
        # index to cluster
        cluster_map={row_i: lbl for row_i,lbl in zip(idxs,labels)}
        for row_i,r in enumerate(all_rows):
            cluster_id=cluster_map.get(row_i,-1)
            body=(r.get('body') or '').strip()
            toks=body.split()
            token_len=len(toks)
            # Simple length bucket replicate (avoid importing earlier code)
            if token_len<=40: lb='short'
            elif token_len<=120: lb='medium'
            else: lb='long'
            qflag=1 if '?' in body else 0
            sentiment='neu'
            w.writerow([
                r.get('id'),
                r.get('transition'),
                r.get('pre_post'),
                r.get('subreddit'),
                r.get('score_bucket'),
                lb,
                qflag,
                sentiment,
                cluster_id,
                token_len
            ])
    print(f'Clusters assigned k={k} -> {cluster_csv} ; enriched frame -> {enriched_path}')

if __name__=='__main__':
    main()
