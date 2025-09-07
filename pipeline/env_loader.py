"""Lightweight .env loader (no external dependency).

If REDDIT_CLIENT_ID not in environment, attempts to parse a .env file in the
project root (parent of this script) and inject variables. Lines beginning with
# are ignored. Only KEY=VALUE patterns are considered. Existing variables are
not overwritten.
"""
from __future__ import annotations
import os, pathlib

def load_env_once():
    if os.getenv('REDDIT_CLIENT_ID') and os.getenv('REDDIT_CLIENT_SECRET'):
        return
    root = pathlib.Path(__file__).resolve().parent.parent
    env_path = root / '.env'
    if not env_path.exists():
        return
    try:
        with open(env_path,'r',encoding='utf-8') as f:
            for line in f:
                line=line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k,v = line.split('=',1)
                k=k.strip(); v=v.strip()
                if k and v and k not in os.environ:
                    os.environ[k]=v
    except Exception:
        pass

if __name__ == '__main__':  # manual test
    load_env_once()
    print('Loaded CID present:', bool(os.getenv('REDDIT_CLIENT_ID')))
