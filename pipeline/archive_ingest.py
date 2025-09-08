#!/usr/bin/env python3
"""Archive ingestion for historical Reddit comments (local dumps).

Purpose:
  Provide a purely local, transparent pathway to recover historical windows
  now unreachable through live Reddit API search. Accepts a set of compressed
  dump files (Pushshift-style comment dumps) and filters records by:
	* subreddit membership (case-insensitive match)
	* created_utc within inclusive [start, end] epoch window

Output schema (JSONL):
  id, parent_id, link_id, created_utc, score, body, subreddit, author

Design:
  * Stream decompression (zstandard or xz) to avoid large memory usage.
  * Heuristically detect JSON object per line. Skip malformed lines with log.
  * Optional progress logging every N lines.
  * Support multiple input files (concatenate logically). Order not guaranteed;
	caller can sort later if desired.

Example:
  python pipeline/archive_ingest.py \
	--inputs /data/pushshift/RC_2024-04.zst /data/pushshift/RC_2024-05.zst \
	--subreddits ChatGPT OpenAI \
	--start 2024-04-29T00:00:00Z --end 2024-05-12T23:59:59Z \
	--out pipeline/data/gpt4_to_4o_pre.jsonl

Notes:
  * Does not perform keyword filtering; upstream analysis handles lexical focus.
  * Accepts both lowercase and mixed-case subreddit names. Internally normalizes
	to the canonical letter case found in the dump if present.
  * This module intentionally avoids external dependencies beyond zstandard for
	performance and transparency.
"""
from __future__ import annotations
import argparse, os, sys, json, gzip, lzma, time
from datetime import datetime, timezone
from typing import Iterable, List, Dict, Set

try:
	import zstandard as zstd  # type: ignore
except ImportError:  # pragma: no cover
	zstd = None


def parse_args():
	ap = argparse.ArgumentParser()
	ap.add_argument('--inputs', nargs='+', required=True, help='List of local dump files (.zst, .xz, .lzma, .gz, .jsonl)')
	ap.add_argument('--subreddits', nargs='+', required=True)
	ap.add_argument('--start', required=True, help='ISO UTC e.g. 2024-04-29T00:00:00Z')
	ap.add_argument('--end', required=True, help='ISO UTC inclusive end')
	ap.add_argument('--out', required=True)
	ap.add_argument('--log-every', type=int, default=250000, help='Progress log frequency (lines)')
	ap.add_argument('--max', type=int, default=0, help='Optional cap on accepted rows (0 = no cap)')
	return ap.parse_args()


def iso_to_epoch(iso: str) -> int:
	return int(datetime.strptime(iso.replace('Z',''), '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc).timestamp())


def open_stream(path: str):
	lower = path.lower()
	if lower.endswith('.zst'):
		if zstd is None:
			raise SystemExit('zstandard not installed but .zst file encountered')
		fh = open(path,'rb')
		dctx = zstd.ZstdDecompressor(max_window_size=2**31)
		return dctx.stream_reader(fh)
	if lower.endswith('.xz') or lower.endswith('.lzma'):
		return lzma.open(path,'rb')
	if lower.endswith('.gz'):
		return gzip.open(path,'rb')
	return open(path,'rb')  # raw


def iter_lines(path: str):
	with open_stream(path) as fh:
		for raw in fh:
			try:
				yield raw.decode('utf-8','replace').rstrip('\n')
			except Exception:
				continue


ESSENTIAL_FIELDS = {'id','parent_id','link_id','created_utc','body','subreddit','author'}


def normalize(obj: Dict) -> Dict:
	# Provide safe defaults; assume obj maybe pushshift-style
	return {
		'id': obj.get('id'),
		'parent_id': obj.get('parent_id'),
		'link_id': obj.get('link_id') or obj.get('link_id_fullname') or obj.get('submission_id') or obj.get('link_id') or None,
		'created_utc': int(obj.get('created_utc', 0) or 0),
		'score': int(obj.get('score', 0) or 0),
		'body': obj.get('body') or '',
		'subreddit': obj.get('subreddit'),
		'author': str(obj.get('author','anon'))
	}


def accept(obj: Dict, subs_lc: Set[str], start_ts: int, end_ts: int) -> bool:
	try:
		sr = str(obj.get('subreddit','')).lower()
		if sr not in subs_lc:
			return False
		ts = int(obj.get('created_utc',0) or 0)
		if ts < start_ts or ts > end_ts:
			return False
		return True
	except Exception:
		return False


def main():
	args = parse_args()
	start_ts = iso_to_epoch(args.start)
	end_ts = iso_to_epoch(args.end)
	subs_lc = {s.lower() for s in args.subreddits}
	accepted=0
	total=0
	malformed=0
	seen_ids=set()
	cap = args.max if args.max>0 else None
	t0=time.time()
	out_path=args.out
	os.makedirs(os.path.dirname(out_path), exist_ok=True)
	with open(out_path,'w',encoding='utf-8') as outf:
		for path in args.inputs:
			print(f"[scan] {path}")
			for line in iter_lines(path):
				total+=1
				if not line or line.startswith('{') is False:
					continue
				try:
					obj=json.loads(line)
				except Exception:
					malformed+=1
					continue
				if accept(obj, subs_lc, start_ts, end_ts):
					norm=normalize(obj)
					cid=norm['id']
					if not cid or cid in seen_ids:
						continue
					seen_ids.add(cid)
					outf.write(json.dumps(norm)+'\n')
					accepted+=1
					if cap and accepted>=cap:
						print('[cap] reached; stopping early')
						break
				if total % args.log_every == 0:
					rate = total / max(1,(time.time()-t0))
					print(f"[progress] lines={total} accepted={accepted} malformed={malformed} rate={rate:.1f}/s")
			if cap and accepted>=cap:
				break
	dur=time.time()-t0
	print(f"Done. lines={total} accepted={accepted} malformed={malformed} unique_ids={len(seen_ids)} elapsed={dur:.1f}s -> {out_path}")


if __name__=='__main__':
	main()

