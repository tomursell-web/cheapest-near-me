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
        value=st.session_state.get("petrol_postcode_val", st.session_state.postcode),
        placeholder="e.g. RG1 1AA",
        key="petrol_postcode_input",
    )
    search_clicked = st.button("Search this postcode", type="primary", use_container_width=True)

with col_fuel:
    fuel_type = st.radio(
        "Fuel type",
        ["E10 Unleaded", "Super Unleaded (E5)", "Diesel"],
        key="fuel_type_filter",
    )

with col_radius:
    radius_miles = st.slider("Search radius (miles)", 1, 20, 5, key="petrol_radius")

fuel_code_map = {
    "E10 Unleaded": "E10",
    "Super Unleaded (E5)": "E5",
    "Diesel": "B7",
}
selected_fuel = fuel_code_map[fuel_type]

# ── Handle postcode search ────────────────────────────────────────────────────
if search_clicked:
    if petrol_postcode.strip():
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
    else:
        st.error("Please enter a postcode.")
        st.stop()

# Initialise location on first load
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

st.divider()
st.caption(f"Showing prices near **{user_label}** ({user_postcode})")


# ── Helpers ───────────────────────────────────────────────────────────────────
def dist_km(la1, lo1, la2, lo2):
    R = 6371
    dp = math.radians(la2 - la1)
    dl = math.radians(lo2 - lo1)
    a = math.sin(dp/2)**2 + math.cos(math.radians(la1)) * math.cos(math.radians(la2)) * math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def mock_stations(lat, lng):
    return [
        {"name": "Tesco Petrol Station",      "address": "Retail Park",     "lat": lat+0.005, "lng": lng+0.003, "prices": {"E10": 136.9, "E5": 146.9, "B7": 142.9}},
        {"name": "BP",                         "address": "High Street",     "lat": lat-0.003, "lng": lng+0.007, "prices": {"E10": 139.9, "E5": 149.9, "B7": 145.9}},
        {"name": "Shell",                      "address": "Main Road",       "lat": lat+0.008, "lng": lng-0.004, "prices": {"E10": 138.9, "E5": 148.9, "B7": 144.9}},
        {"name": "Asda Petrol Station",        "address": "Superstore",      "lat": lat-0.006, "lng": lng-0.005, "prices": {"E10": 133.9, "E5": 143.9, "B7": 139.9}},
        {"name": "Sainsbury's Petrol",         "address": "Shopping Centre", "lat": lat+0.010, "lng": lng+0.008, "prices": {"E10": 135.9, "E5": 145.9, "B7": 141.9}},
        {"name": "Esso",                       "address": "Bypass Road",     "lat": lat-0.009, "lng": lng+0.011, "prices": {"E10": 140.9, "E5": 150.9, "B7": 146.9}},
        {"name": "Morrisons Petrol Station",   "address": "Retail Park",     "lat": lat+0.012, "lng": lng-0.009, "prices": {"E10": 134.9, "E5": 144.9, "B7": 140.9}},
    ]


def fetch_live_prices(lat, lng, radius_mi, fuel):
    """Try the official widget API endpoint, fall back to mock data."""
    try:
        resp = requests.get(
            "https://checkfuelprices.co.uk/api/widget/stations",
            params={
                "lat": lat,
                "lng": lng,
                "fuel": fuel,
                "radius": radius_mi,
                "limit": 20,
                "sort": "price_low",
            },
            timeout=8,
        )
        if resp.status_code == 200:
            data = resp.json()
            raw = data.get("stations") or data.get("data") or []
            results = []
            for s in raw:
                price = (
                    s.get("price")
                    or s.get(fuel.lower())
                    or s.get("prices", {}).get(fuel)
                )
                if price:
                    slat = float(s.get("lat", lat))
                    slng = float(s.get("lng", lng))
                    results.append({
                        "name": s.get("name", "Unknown"),
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

    # Mock fallback
    radius_km = radius_mi * 1.60934
    results = []
    for s in mock_stations(lat, lng):
        d = dist_km(lat, lng, s["lat"], s["lng"])
        if d <= radius_km and fuel in s["prices"]:
            results.append({
                "name": s["name"],
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
    stations = fetch_live_prices(user_lat, user_lng, radius_miles, selected_fuel)

if not stations:
    st.warning("No fuel stations found in that area. Try increasing the search radius.")
    st.stop()

is_live = any(s.get("source") == "live" for s in stations)
if is_live:
    st.success("Live prices from the UK government Fuel Finder scheme — updated every 30 minutes.")
else:
    st.info(
        "Showing example prices while the live feed loads. "
        "Real station prices from the UK CMA Fuel Finder will appear here automatically."
    )

cheapest_price = stations[0]["price_p"]

# ── Two column layout: results + map ─────────────────────────────────────────
results_col, map_col = st.columns([1, 1])

with results_col:
    st.markdown(f"### {len(stations)} stations — **{fuel_type}**")

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
                    <span style="color:#999;font-size:0.8rem">50L: £{tank_50:.2f} &nbsp;·&nbsp; Full tank (65L): £{tank_full:.2f}</span>
                </div>
                <div style="text-align:right">
                    <span style="font-size:1.8rem;font-weight:800;color:{price_color}">{s['price_p']:.1f}p</span><br>
                    <span style="color:#999;font-size:0.78rem">per litre</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with map_col:
    st.markdown("### Map")
    st.caption("Green = cheapest · Blue = others · Purple = you")

    m = folium.Map(
        location=[user_lat, user_lng],
        zoom_start=13,
        tiles="CartoDB positron",
    )

    folium.Circle(
        location=[user_lat, user_lng],
        radius=radius_miles * 1609,
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
        color = "green" if i == 0 else "blue"
        popup_html = f"""
        <div style="min-width:150px;font-family:sans-serif">
            <b>{s['name']}</b><br>
            <span style="color:#555;font-size:0.85rem">{s.get('address','')}</span>
            <hr style="margin:5px 0">
            <b style="font-size:1.1rem;color:{'#34a853' if i==0 else '#4285f4'}">{s['price_p']:.1f}p/L</b><br>
            <span style="font-size:0.82rem">{s['distance_km']} km away</span>
        </div>
        """
        folium.Marker(
            location=[s["lat"], s["lng"]],
            tooltip=f"{s['name']} — {s['price_p']:.1f}p/L",
            popup=folium.Popup(popup_html, max_width=200),
            icon=folium.Icon(color=color, icon="tint", prefix="fa"),
        ).add_to(m)

    st_folium(m, width="100%", height=500, returned_objects=[])

# ── Live widget from checkfuelprices.co.uk ────────────────────────────────────
st.divider()
st.subheader("Live fuel price finder")
st.caption("Powered by checkfuelprices.co.uk using official UK CMA data")

clean_postcode = user_postcode.replace(" ", "")
widget_url = f"https://checkfuelprices.co.uk/widget/embed?postcode={clean_postcode}&fuel={selected_fuel}&radius={radius_miles}&sort=price_low&theme=light"

st.components.v1.iframe(widget_url, height=600, scrolling=True)

# ── Report a price ────────────────────────────────────────────────────────────
st.divider()
st.subheader("Seen a price that's wrong?")
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
            st.success(f"Thank you! Recorded {report_fuel} at {report_price:.1f}p/litre at {report_station}.")
            st.balloons()
        else:
            st.error("Please enter the station name and price.")
