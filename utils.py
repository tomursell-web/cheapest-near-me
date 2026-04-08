"""Shared utilities — imported by app.py and all pages."""

import json
import math
import os
import uuid

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Geometry ──────────────────────────────────────────────────────────────────

def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    dφ = math.radians(lat2 - lat1)
    dλ = math.radians(lng2 - lng1)
    a = math.sin(dφ / 2) ** 2 + math.cos(φ1) * math.cos(φ2) * math.sin(dλ / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def distance_words(km: float) -> str:
    if km < 0.10:
        return "just round the corner"
    if km < 0.5:
        return f"about {int(round(km * 1000, -2))} metres away"
    if km < 1.2:
        return "less than a mile away"
    miles = km * 0.621371
    if miles < 2:
        return f"about {miles:.1f} miles away"
    return f"about {miles:.0f} miles away"


# ── Postcode lookup (postcodes.io — free, no key needed) ─────────────────────

def lookup_postcode(postcode: str) -> tuple[float, float, str]:
    """Return (lat, lng, district_label). Raises ValueError if not found."""
    clean = postcode.strip().upper().replace(" ", "")
    try:
        resp = requests.get(
            f"https://api.postcodes.io/postcodes/{clean}",
            timeout=5,
        )
    except Exception:
        raise ValueError("Could not reach the postcode service. Please check your internet connection.")

    if resp.status_code == 404:
        raise ValueError(f"'{postcode.upper()}' doesn't look like a valid postcode.")
    if resp.status_code != 200:
        raise ValueError("The postcode service is unavailable right now.")

    data = resp.json()
    if data.get("status") != 200 or not data.get("result"):
        raise ValueError(f"'{postcode.upper()}' doesn't look like a valid postcode.")

    result = data["result"]
    label = result.get("admin_district") or result.get("region") or postcode.upper()
    return float(result["latitude"]), float(result["longitude"]), label


# ── AI search (Claude Haiku) ──────────────────────────────────────────────────

_AI_SYSTEM = """You help users find products in local shops.
Given a search term (may be a brand name, colloquial term, or generic product), respond with valid JSON only — no markdown, no explanation, no code fences.
Schema:
{
  "search_terms": ["term1", "term2"],
  "category": "Groceries|Pharmacy|Hardware|Household|null",
  "friendly_message": "Searching for X near you..."
}
Rules:
- search_terms: 1–4 generic product names that a UK shop would stock. Use common names, not brand names.
- category: pick the single most likely category, or null if unclear.
- friendly_message: warm, plain English sentence (max 10 words), e.g. "Searching for steering wheel locks near you..."
Examples:
"Stoplock"    → {"search_terms":["steering wheel lock","car immobiliser"],"category":"Hardware","friendly_message":"Searching for steering wheel locks near you..."}
"Calpol"      → {"search_terms":["children's paracetamol","pain relief syrup"],"category":"Pharmacy","friendly_message":"Searching for children's pain relief near you..."}
"Fairy"       → {"search_terms":["washing up liquid","dish soap"],"category":"Household","friendly_message":"Searching for washing up liquid near you..."}
"WD40"        → {"search_terms":["WD-40","lubricant spray","penetrating oil"],"category":"Hardware","friendly_message":"Searching for lubricant spray near you..."}
"paracetamol" → {"search_terms":["paracetamol"],"category":"Pharmacy","friendly_message":"Searching for paracetamol near you..."}"""


def ai_interpret_search(query: str) -> dict:
    """Use Claude Haiku to expand the search. Falls back to plain search if no key."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    fallback = {
        "search_terms": [query.lower()],
        "category": None,
        "friendly_message": f'Searching for "{query}" near you...',
    }
    if not api_key:
        return fallback

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            system=_AI_SYSTEM,
            messages=[{"role": "user", "content": query}],
        )
        text = msg.content[0].text.strip()
        # Strip markdown code fences if the model wraps the JSON
        if "```" in text:
            parts = text.split("```")
            text = parts[1] if len(parts) > 1 else parts[0]
            if text.startswith("json"):
                text = text[4:]
        result = json.loads(text.strip())
        # Ensure required keys exist
        result.setdefault("search_terms", [query.lower()])
        result.setdefault("category", None)
        result.setdefault("friendly_message", f'Searching for "{query}" near you...')
        return result
    except Exception:
        return fallback


# ── Session state initialisation ──────────────────────────────────────────────

def init_session():
    defaults = {
        "postcode":       "SW1A 1AA",
        "user_lat":       51.5074,
        "user_lng":       -0.1278,
        "postcode_label": "Central London",
        "basket":         [],
        "search_query":   "",
        "search_result":  None,   # dict from ai_interpret_search
        "session_id":     str(uuid.uuid4()),
        "votes":          {},     # price_id -> 1 or -1
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Shared sidebar ────────────────────────────────────────────────────────────

def render_sidebar():
    init_session()
    with st.sidebar:
        st.markdown("## 🛒 Cheapest Near Me")
        st.caption("Find the best price near you.")
        st.divider()

        # Postcode
        st.markdown("**📍 Your location**")
        pc_input = st.text_input(
            "Postcode",
            value=st.session_state.postcode,
            label_visibility="collapsed",
            placeholder="e.g. SW1A 1AA",
            key="sidebar_postcode_input",
        )
        if st.button("Update location", use_container_width=True, key="sidebar_update_loc"):
            _update_location(pc_input)

        st.caption(f"Near: **{st.session_state.postcode_label}**")
        st.divider()

        # Basket
        n = len(st.session_state.basket)
        st.markdown(f"**🧺 Basket ({n} item{'s' if n != 1 else ''})**")
        if st.session_state.basket:
            for item in list(st.session_state.basket):
                c1, c2 = st.columns([5, 1])
                c1.write(item["name"])
                if c2.button("✕", key=f"sb_rm_{item['id']}", help="Remove"):
                    st.session_state.basket = [
                        x for x in st.session_state.basket if x["id"] != item["id"]
                    ]
                    st.rerun()
            st.write("")
            if st.button("Clear basket", type="secondary", use_container_width=True):
                st.session_state.basket = []
                st.rerun()
        else:
            st.caption("Nothing added yet.")


def _update_location(postcode: str):
    if not postcode.strip():
        st.sidebar.warning("Please enter a postcode.")
        return
    try:
        lat, lng, label = lookup_postcode(postcode)
        st.session_state.postcode       = postcode.strip().upper()
        st.session_state.user_lat       = lat
        st.session_state.user_lng       = lng
        st.session_state.postcode_label = label
        st.sidebar.success(f"Location set to {label}.")
    except ValueError as e:
        st.sidebar.error(str(e))


# ── DB helpers (Supabase with mock fallback) ──────────────────────────────────

def db_search_products(terms: list[str], category: str | None = None) -> list[dict]:
    try:
        from database.supabase_client import get_client
        client = get_client()
        results = []
        seen = set()
        for term in terms:
            resp = (
                client.table("products")
                .select("*")
                .ilike("name", f"%{term}%")
                .limit(10)
                .execute()
            )
            for row in resp.data or []:
                if row["id"] not in seen:
                    results.append(row)
                    seen.add(row["id"])
        return results
    except Exception:
        pass
    from database.mock_data import search_products
    return search_products(terms, category)


def db_get_price_rows(product_id: str) -> list[dict]:
    lat = st.session_state.get("user_lat", 51.5074)
    lng = st.session_state.get("user_lng", -0.1278)
    try:
        from database.supabase_client import get_client
        client = get_client()
        resp = (
            client.table("prices")
            .select("*, shops(*)")
            .eq("product_id", product_id)
            .execute()
        )
        rows = []
        for row in resp.data or []:
            shop = row.get("shops", {})
            dist = haversine(lat, lng, shop.get("lat", lat), shop.get("lng", lng))
            rows.append({
                "shop_id":  shop.get("id", ""),
                "shop":     shop.get("name", "Unknown shop"),
                "address":  shop.get("address", ""),
                "lat":      shop.get("lat", lat),
                "lng":      shop.get("lng", lng),
                "price":    float(row["price"]),
                "distance": round(dist, 2),
            })
        return sorted(rows, key=lambda r: (r["price"], r["distance"]))
    except Exception:
        pass
    from database.mock_data import get_price_rows
    return get_price_rows(product_id, lat, lng)
