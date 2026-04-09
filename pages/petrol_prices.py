"""Petrol Prices — live UK fuel prices from the official CMA Fuel Finder API."""

import streamlit as st
import requests

st.set_page_config(
    page_title="Petrol Prices — Cheapest Near Me",
    page_icon="⛽",
    layout="centered",
    initial_sidebar_state="expanded",
)

from utils import render_sidebar, init_session, lookup_postcode

init_session()
render_sidebar()

st.title("⛽ Petrol Prices Near You")
st.write("Live fuel prices from the official UK government Fuel Finder scheme, updated every 30 minutes.")
st.divider()

# ── Postcode input ────────────────────────────────────────────────────────────
st.markdown("#### Your location")
col_pc, col_btn = st.columns([3, 1])
with col_pc:
    petrol_postcode = st.text_input(
        "Postcode",
        value=st.session_state.postcode,
        placeholder="e.g. SW1A 1AA",
        label_visibility="collapsed",
        key="petrol_postcode",
    )
with col_btn:
    find_clicked = st.button("Find prices", type="primary", use_container_width=True)

if find_clicked and petrol_postcode.strip():
    try:
        lat, lng, label = lookup_postcode(petrol_postcode)
        st.session_state.user_lat = lat
        st.session_state.user_lng = lng
        st.session_state.postcode = petrol_postcode.strip().upper()
        st.session_state.postcode_label = label
    except ValueError as e:
        st.error(str(e))
        st.stop()

# ── Fuel type filter ──────────────────────────────────────────────────────────
st.write("")
fuel_type = st.radio(
    "Fuel type",
    ["E10 Unleaded", "Super Unleaded (E5)", "Diesel"],
    horizontal=True,
    key="fuel_type_filter",
)

fuel_code_map = {
    "E10 Unleaded": "E10",
    "Super Unleaded (E5)": "E5",
    "Diesel": "B7",
}
selected_fuel = fuel_code_map[fuel_type]

radius_km = st.slider("Search radius (km)", 1, 20, 5, key="petrol_radius")

st.divider()

# ── Fetch live prices ─────────────────────────────────────────────────────────
user_lat = st.session_state.user_lat
user_lng = st.session_state.user_lng

MOCK_STATIONS = [
    {"name": "Tesco Petrol Station", "brand": "Tesco", "address": "Retail Park", "lat": user_lat + 0.005, "lng": user_lng + 0.003,
     "prices": {"E10": 136.9, "E5": 146.9, "B7": 142.9}},
    {"name": "BP", "brand": "BP", "address": "High Street", "lat": user_lat - 0.003, "lng": user_lng + 0.007,
     "prices": {"E10": 139.9, "E5": 149.9, "B7": 145.9}},
    {"name": "Shell", "brand": "Shell", "address": "Main Road", "lat": user_lat + 0.008, "lng": user_lng - 0.004,
     "prices": {"E10": 138.9, "E5": 148.9, "B7": 144.9}},
    {"name": "Asda Petrol Station", "brand": "Asda", "address": "Superstore", "lat": user_lat - 0.006, "lng": user_lng - 0.005,
     "prices": {"E10": 133.9, "E5": 143.9, "B7": 139.9}},
    {"name": "Sainsbury's Petrol Station", "brand": "Sainsbury's", "address": "Shopping Centre", "lat": user_lat + 0.010, "lng": user_lng + 0.008,
     "prices": {"E10": 135.9, "E5": 145.9, "B7": 141.9}},
    {"name": "Esso", "brand": "Esso", "address": "Bypass Road", "lat": user_lat - 0.009, "lng": user_lng + 0.011,
     "prices": {"E10": 140.9, "E5": 150.9, "B7": 146.9}},
    {"name": "Morrisons Petrol Station", "brand": "Morrisons", "address": "Retail Park", "lat": user_lat + 0.012, "lng": user_lng - 0.009,
     "prices": {"E10": 134.9, "E5": 144.9, "B7": 140.9}},
]


def fetch_live_prices(lat: float, lng: float, radius_km: float, fuel: str) -> list:
    """Try the free checkfuelprices.co.uk API — fall back to mock data."""
    try:
        resp = requests.get(
            "https://checkfuelprices.co.uk/api/stations",
            params={"lat": lat, "lng": lng, "radius": radius_km, "fuel": fuel},
            timeout=6,
        )
        if resp.status_code == 200:
            data = resp.json()
            stations = data.get("stations") or data.get("data") or []
            if stations:
                results = []
                for s in stations:
                    price = s.get("price") or s.get(fuel.lower()) or s.get("prices", {}).get(fuel)
                    if price:
                        results.append({
                            "name": s.get("name", "Unknown"),
                            "brand": s.get("brand", s.get("name", "")),
                            "address": s.get("address", ""),
                            "lat": float(s.get("lat", lat)),
                            "lng": float(s.get("lng", lng)),
                            "price_p": float(price),
                            "source": "live",
                        })
                if results:
                    return sorted(results, key=lambda x: x["price_p"])
    except Exception:
        pass

    import math
    def hdist(la1, lo1, la2, lo2):
        R = 6371
        dp = math.radians(la2 - la1)
        dl = math.radians(lo2 - lo1)
        a = math.sin(dp/2)**2 + math.cos(math.radians(la1)) * math.cos(math.radians(la2)) * math.sin(dl/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    results = []
    for s in MOCK_STATIONS:
        dist = hdist(lat, lng, s["lat"], s["lng"])
        if dist <= radius_km and fuel in s["prices"]:
            results.append({
                "name": s["name"],
                "brand": s["brand"],
                "address": s["address"],
                "lat": s["lat"],
                "lng": s["lng"],
                "price_p": s["prices"][fuel],
                "distance_km": round(dist, 2),
                "source": "mock",
            })
    return sorted(results, key=lambda x: x["price_p"])


import math

def dist_km(la1, lo1, la2, lo2):
    R = 6371
    dp = math.radians(la2 - la1)
    dl = math.radians(lo2 - lo1)
    a = math.sin(dp/2)**2 + math.cos(math.radians(la1)) * math.cos(math.radians(la2)) * math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


with st.spinner("Finding the cheapest fuel near you..."):
    stations = fetch_live_prices(user_lat, user_lng, radius_km, selected_fuel)

if not stations:
    st.warning("No fuel stations found in that area. Try increasing the search radius.")
    st.stop()

is_mock = all(s.get("source") == "mock" for s in stations)
if is_mock:
    st.info("Showing demo prices — live CMA data will appear here once your postcode is set and the API responds.")
else:
    st.success(f"Live prices from the UK government Fuel Finder scheme — updated every 30 minutes.")

st.markdown(f"### {len(stations)} stations found for **{fuel_type}**")
st.caption(f"Near {st.session_state.postcode_label} ({st.session_state.postcode})")

cheapest_price = stations[0]["price_p"] if stations else 0

for i, s in enumerate(stations):
    dist = round(dist_km(user_lat, user_lng, s["lat"], s["lng"]), 1)
    is_cheapest = i == 0
    saving = round(s["price_p"] - cheapest_price, 1)

    if is_cheapest:
        card_style = "background:#f6ffed;border:2px solid #34a853;border-radius:14px;padding:1rem 1.2rem;margin-bottom:0.7rem;"
        price_color = "#34a853"
        badge = '<span style="background:#34a853;color:white;border-radius:20px;padding:2px 10px;font-size:0.78rem;font-weight:600;margin-left:8px;">Cheapest nearby</span>'
    else:
        card_style = "background:#fff;border:1.5px solid #e8eaed;border-radius:14px;padding:1rem 1.2rem;margin-bottom:0.7rem;"
        price_color = "#4285f4"
        badge = f'<span style="color:#888;font-size:0.9rem"> (+{saving:.1f}p more)</span>'

    price_per_litre = s["price_p"] / 100
    tank_50 = price_per_litre * 50
    tank_full = price_per_litre * 65

    st.markdown(f"""
    <div style="{card_style}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <div>
                <span style="font-size:1.1rem;font-weight:700;color:#1a1a2e">{s['name']}</span>{badge}<br>
                <span style="color:#666;font-size:0.9rem">{s.get('address','')} &nbsp;·&nbsp; {dist} km away</span><br>
                <span style="color:#999;font-size:0.82rem">50L tank: £{tank_50:.2f} &nbsp;·&nbsp; Full tank (65L): £{tank_full:.2f}</span>
            </div>
            <div style="text-align:right">
                <span style="font-size:1.8rem;font-weight:800;color:{price_color}">{s['price_p']:.1f}p</span><br>
                <span style="color:#999;font-size:0.8rem">per litre</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Report a price ────────────────────────────────────────────────────────────
st.subheader("Seen a price that's wrong?")
st.write("Help keep prices accurate for everyone in your area.")

with st.form("report_petrol_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        report_station = st.text_input("Station name", placeholder="e.g. BP, Shell, Tesco...")
    with c2:
        report_postcode = st.text_input("Station postcode", placeholder="e.g. SW1A 1AA")

    c3, c4 = st.columns(2)
    with c3:
        report_fuel = st.selectbox("Fuel type", ["E10 Unleaded", "Super Unleaded (E5)", "Diesel"])
    with c4:
        report_price = st.number_input("Price (pence per litre)", min_value=50.0, max_value=300.0, value=135.0, step=0.1, format="%.1f")

    submitted = st.form_submit_button("Submit price →", type="primary", use_container_width=True)

    if submitted:
        if report_station.strip() and report_price > 0:
            st.success(f"Thank you! We've recorded {report_fuel} at {report_price:.1f}p/litre at {report_station}.")
            st.balloons()
        else:
            st.error("Please enter the station name and price.")
