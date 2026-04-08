"""Supabase connection helper."""

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@lru_cache(maxsize=1)
def get_client():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_ANON_KEY", "")
    if not url or not key or "your-project" in url:
        raise RuntimeError("Supabase not configured.")
    from supabase import create_client
    return create_client(url, key)


def is_configured() -> bool:
    try:
        get_client()
        return True
    except Exception:
        return False
