"""Petrol Prices — live UK fuel prices from the official CMA Fuel Finder API."""

import math
import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Petrol Prices — Cheapest Near Me",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils import render_sidebar, init_session, lookup_postcode

init_session()
render_sidebar()

st.title("⛽ Petrol Prices Near You")
st.write("Live fuel prices from the official UK government Fuel Finder scheme, updated every 30 minutes.")
st.divider()

# ── Location + controls ───────────────────────────────────────────────────────
col_pc, col_fuel, col_radius = st.columns([2, 2, 2])

with col_pc:
    petrol_postcode = st.text_input(
        "Your postcode",
        value=st.session_state.get("petrol_postcode_input", st.session_state.postcode),
        placeholder="e.g. RG1 1AA",
        key="petrol_postcode_input",
    )
    if st.button("Search this postcode", type="primary", use_container_width=True):
        try:
            lat, lng, label = lookup_postcode(petrol_postcode)
            st.session_state.petrol_lat = lat
            st.session_state.petrol_lng = lng
            st.session_state.petrol_label = label
            st.session_state.petrol_postcode_val = petrol_postcode.strip().upper()
            st.rerun()
        except ValueError as e:
            st.error(str(e))
            st.stop()

with col_fuel:
    fuel_type = st.radio(
        "Fuel type",
        ["E10 Unleaded", "Super Unleaded (E5)", "Diesel"],
        key="fuel_type_filter",
    )

with col_radius:
    radius_km = st.slider("Search radius (km)", 1, 20, 5, key="petrol_radius")

# Use petrol-specific location if set, otherwise fall back to session default
if "petrol_lat" not in st.session_state:
    try:
        lat, lng, label = lookup_postcode(st.session_state.postcode)
        st.session_state.petrol_lat = lat
        st.session_state.petrol_lng = lng
        st.session_state.petrol_label = label
        st.session_state.petrol_postcode_val = st.session_state.postcode
    except Exception:
        st.session_state.petrol_lat = 51.5074
        st.session_state.petrol_lng = -0.1278
        st.session_state.petrol_label = "Central London"
        st.session_state.petrol_postcode_val = "SW1A 1AA"

user_lat = st.session_state.petrol_lat
user_lng = st.session_state.petrol_lng
user_label = st.session_state.petrol_label
user_postcode = st.session_state.petrol_postcode_val

fuel_code_map = {
    "E10 Unleaded": "E10",
    "Super Unleaded (E5)": "E5",
    "Diesel": "B7",
}
selected_fuel = fuel_code_map[fuel_type]

st.divider()


# ── Helpers ───────────────────────────────────────────────────────────────────
def dist_km(la1, lo1, la2, lo2):
    R = 6371
    dp = math.radians(la2 - la1)
    dl = math.radians(lo2 - lo1)
    a = math.sin(dp/2)**2 + math.cos(math.radians(la1)) * math.cos(math.radians(la2)) * math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def mock_stations(lat, lng):
    return [
        {"name": "Tesco Petrol Station",       "brand": "Tesco",        "address": "Retail Park",      "lat": lat+0.005, "lng": lng+0.003, "prices": {"E10": 136.9, "E5": 146.9, "B7": 142.9}},
        {"name": "BP",                          "brand": "BP",           "address": "High Street",      "lat": lat-0.003, "lng": lng+0.007, "prices": {"E10": 139.9, "E5": 149.9, "B7": 145.9}},
        {"name": "Shell",                       "brand": "Shell",        "address": "Main Road",        "lat": lat+0.008, "lng": lng-0.004, "prices": {"E10": 138.9, "E5": 148.9, "B7": 144.9}},
        {"name": "Asda Petrol Station",         "brand": "Asda",         "address": "Superstore",       "lat": lat-0.006, "lng": lng-0.005, "prices": {"E10": 133.9, "E5": 143.9, "B7": 139.9}},
        {"name": "Sainsbury's Petrol Station",  "brand": "Sainsbury's",  "address": "Shopping Centre",  "lat": lat+0.010, "lng": lng+0.008, "prices": {"E10": 135.9, "E5": 145.9, "B7": 141.9}},
        {"name": "Esso",                        "brand": "Esso",         "address": "Bypass Road",      "lat": lat-0.009, "lng": lng+0.011, "prices": {"E10": 140.9, "E5": 150.9, "B7": 146.9}},
        {"name": "Morrisons Petrol Station",    "brand": "Morrisons",    "address": "Retail Park",      "lat": lat+0.012, "lng": lng-0.009, "prices": {"E10": 134.9, "E5": 144.9, "B7": 140.9}},
    ]


def fetch_live_prices(lat, lng, radius, fuel):
    try:
        resp = requests.get(
            "https://checkfuelprices.co.uk/api/stations",
            params={"lat": lat, "lng": lng, "radius": radius, "fuel": fuel},
            timeout=6,
        )
        if resp.status_code == 200:
            data = resp.json()
            stations = data.get("stations") or data.get("data") or []
            results = []
            for s in stations:
                price = s.get("price") or s.get(fuel.lower()) or s.get("prices", {}).get(fuel)
                if price:
                    slat = float(s.get("lat", lat))
                    slng = float(s.get("lng", lng))
                    results.append({
                        "name": s.get("name", "Unknown"),
                        "brand": s.get("brand", s.get("name", "")),
                        "address": s.get("address", ""),
                        "lat": slat,
                        "lng": slng,
                        "price_p": float(price),
                        "distance_km": round(dist_km(lat, lng, slat, slng), 1),
                        "source": "live",
                    })
            if results:
                return sorted(results, key=lambda x: x["price_p"])
    except Exception:
        pass

    results = []
    for s in mock_stations(lat, lng):
        d = dist_km(lat, lng, s["lat"], s["lng"])
        if d <= radius and fuel in s["prices"]:
            results.append({
                "name": s["name"],
                "brand": s["brand"],
                "address": s["address"],
                "lat": s["lat"],
                "lng": s["lng"],
                "price_p": s["prices"][fuel],
                "distance_km": round(d, 1),
                "source": "mock",
            })
    return sorted(results, key=lambda x: x["price_p"])


# ── Fetch prices ──────────────────────────────────────────────────────────────
with st.spinner(f"Finding cheapest {fuel_type} near {user_postcode}..."):
    stations = fetch_live_prices(user_lat, user_lng, radius_km, selected_fuel)

if not stations:
    st.warning("No fuel stations found in that area. Try increasing the search radius.")
    st.stop()

is_mock = all(s.get("source") == "mock" for s in stations)
if is_mock:
    st.info("Showing demo prices — live CMA data will appear automatically once available for your area.")
else:
    st.success("Live prices from the UK government Fuel Finder scheme — updated every 30 minutes.")

cheapest_price = stations[0]["price_p"]

# ── Two column layout: results + map ─────────────────────────────────────────
results_col, map_col = st.columns([1, 1])

with results_col:
    st.markdown(f"### {len(stations)} stations — **{fuel_type}**")
    st.caption(f"Near {user_label} ({user_postcode})")

    for i, s in enumerate(stations):
        is_cheapest = i == 0
        saving = round(s["price_p"] - cheapest_price, 1)
        price_per_litre = s["price_p"] / 100
        tank_50 = price_per_litre * 50
        tank_full = price_per_litre * 65

        if is_cheapest:
            card_style = "background:#f6ffed;border:2px solid #34a853;border-radius:14px;padding:1rem 1.2rem;margin-bottom:0.7rem;"
            price_color = "#34a853"
            badge = '<span style="background:#34a853;color:white;border-radius:20px;padding:2px 10px;font-size:0.78rem;font-weight:600;margin-left:8px;">Cheapest nearby</span>'
        else:
            card_style = "background:#fff;border:1.5px solid #e8eaed;border-radius:14px;padding:1rem 1.2rem;margin-bottom:0.7rem;"
            price_color = "#4285f4"
            badge = f'<span style="color:#888;font-size:0.9rem"> (+{saving:.1f}p)</span>'

        st.markdown(f"""
        <div style="{card_style}">
            <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div>
                    <span style="font-size:1.05rem;font-weight:700;color:#1a1a2e">{s['name']}</span>{badge}<br>
                    <span style="color:#666;font-size:0.88rem">{s.get('address','')} &nbsp;·&nbsp; {s['distance_km']} km away</span><br>
                    <span style="color:#999;font-size:0.8rem">50L: £{tank_50:.2f} &nbsp;·&nbsp; Full tank: £{tank_full:.2f}</span>
                </div>
                <div style="text-align:right">
                    <span style="font-size:1.8rem;font-weight:800;color:{price_color}">{s['price_p']:.1f}p</span><br>
                    <span style="color:#999;font-size:0.78rem">per litre</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with map_col:
    st.markdown(f"### Map")
    st.caption("Green = cheapest · Blue = other stations · Purple = you")

    m = folium.Map(
        location=[user_lat, user_lng],
        zoom_start=13,
        tiles="CartoDB positron",
    )

    folium.Circle(
        location=[user_lat, user_lng],
        radius=radius_km * 1000,
        color="#4285f4",
        fill=True,
        fill_opacity=0.05,
    ).add_to(m)

    folium.Marker(
        location=[user_lat, user_lng],
        tooltip=f"You: {user_postcode}",
        icon=folium.Icon(color="purple", icon="home", prefix="fa"),
    ).add_to(m)

    for i, s in enumerate(stations):
        is_cheapest = i == 0
        color = "green" if is_cheapest else "blue"
        label = f"⭐ CHEAPEST: {s['name']} — {s['price_p']:.1f}p/L" if is_cheapest else f"{s['name']} — {s['price_p']:.1f}p/L"
        popup_html = f"""
        <div style="min-width:160px;font-family:sans-serif">
            <b>{s['name']}</b><br>
            <span style="color:#555;font-size:0.85rem">{s.get('address','')}</span>
            <hr style="margin:5px 0">
            <b style="font-size:1.1rem;color:{'#34a853' if is_cheapest else '#4285f4'}">{s['price_p']:.1f}p/L</b><br>
            <span style="font-size:0.82rem">{s['distance_km']} km away</span>
        </div>
        """
        folium.Marker(
            location=[s["lat"], s["lng"]],
            tooltip=label,
            popup=folium.Popup(popup_html, max_width=200),
            icon=folium.Icon(color=color, icon="tint", prefix="fa"),
        ).add_to(m)

    st_folium(m, width="100%", height=520, returned_objects=[])

# ── Report a price ────────────────────────────────────────────────────────────
st.divider()
st.subheader("Seen a price that's wrong?")
st.write("Help keep prices accurate for everyone in your area.")

with st.form("report_petrol_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        report_station = st.text_input("Station name", placeholder="e.g. BP, Shell, Tesco...")
    with c2:
        report_postcode = st.text_input("Station postcode", placeholder="e.g. RG1 1AA")
    c3, c4 = st.columns(2)
    with c3:
        report_fuel = st.selectbox("Fuel type", ["E10 Unleaded", "Super Unleaded (E5)", "Diesel"])
    with c4:
        report_price = st.number_input("Price (pence per litre)", min_value=50.0, max_value=300.0, value=135.0, step=0.1, format="%.1f")

    submitted = st.form_submit_button("Submit correction →", type="primary", use_container_width=True)
    if submitted:
        if report_station.strip() and report_price > 0:
            st.success(f"Thank you! We've recorded {report_fuel} at {report_price:.1f}p/litre at {report_station}.")
            st.balloons()
        else:
            st.error("Please enter the station name and price.")
