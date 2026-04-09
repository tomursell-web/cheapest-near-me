"""Map View — shows nearby shops as pins on a Folium map."""

import streamlit as st

st.set_page_config(
    page_title="Map View — Cheapest Near Me",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

import folium
from streamlit_folium import st_folium

from utils import render_sidebar, init_session, distance_words, haversine
from database.mock_data import MOCK_SHOPS, PRODUCTS, CATEGORIES, CATEGORY_ICONS

init_session()
render_sidebar()

st.title("🗺️ Shops Near You")
st.caption(
    f"Showing shops near **{st.session_state.postcode_label}** "
    f"({st.session_state.postcode}). "
    "Green pins are the cheapest for your basket."
)

user_lat = st.session_state.user_lat
user_lng = st.session_state.user_lng

col_filter, col_radius = st.columns([3, 2])
with col_filter:
    category_filter = st.selectbox(
        "Show prices for category",
        ["All categories"] + list(CATEGORIES),
        key="map_cat_filter",
    )
with col_radius:
    radius_km = st.slider("Search radius (km)", 0.5, 10.0, 3.0, 0.5, key="map_radius")


def basket_totals_per_shop() -> dict:
    totals = {}
    for item in st.session_state.basket:
        for shop in MOCK_SHOPS:
            if item["id"] in shop["stock"]:
                sid = shop["id"]
                totals[sid] = totals.get(sid, 0.0) + shop["stock"][item["id"]]
    return totals


basket_totals = basket_totals_per_shop()
cheapest_shop_id = min(basket_totals, key=basket_totals.get) if basket_totals else None

nearby_shops = [
    s for s in MOCK_SHOPS
    if haversine(user_lat, user_lng, s["lat"], s["lng"]) <= radius_km
]

m = folium.Map(
    location=[user_lat, user_lng],
    zoom_start=14,
    tiles="CartoDB positron",
    prefer_canvas=True,
)

folium.Circle(
    location=[user_lat, user_lng],
    radius=radius_km * 1000,
    color="#4285f4",
    fill=True,
    fill_opacity=0.06,
    tooltip=f"{radius_km:.1f} km radius",
).add_to(m)

folium.Marker(
    location=[user_lat, user_lng],
    tooltip="You are here",
    popup=f"Your location: {st.session_state.postcode}",
    icon=folium.Icon(color="purple", icon="home", prefix="fa"),
).add_to(m)

for shop in nearby_shops:
    dist = haversine(user_lat, user_lng, shop["lat"], shop["lng"])
    dist_str = distance_words(dist)

    if shop["id"] in basket_totals:
        total = basket_totals[shop["id"]]
        total_str = f"£{total:.2f} for your basket"
        is_cheapest = shop["id"] == cheapest_shop_id
        pin_color = "green" if is_cheapest else "red"
        cheapest_label = " ★ Cheapest!" if is_cheapest else ""
    else:
        total_str = "No basket items"
        pin_color = "blue"
        cheapest_label = ""

    popup_html = f"""
    <div style="min-width:180px;font-family:sans-serif">
        <b style="font-size:1rem">{shop['name']}</b>{cheapest_label}<br>
        <span style="color:#555;font-size:0.85rem">{shop['address']}</span>
        <hr style="margin:6px 0">
        <span style="font-size:0.9rem">
            📍 {dist_str}<br>
            🛒 {total_str}
        </span>
    </div>
    """
    label = f"{shop['name']} — {total_str}" if basket_totals else shop["name"]
    folium.Marker(
        location=[shop["lat"], shop["lng"]],
        popup=folium.Popup(popup_html, max_width=220),
        tooltip=label,
        icon=folium.Icon(color=pin_color, icon="shopping-cart", prefix="fa"),
    ).add_to(m)

map_col, legend_col = st.columns([3, 1])

with map_col:
    st_folium(m, width="100%", height=520, returned_objects=[])

with legend_col:
    st.markdown("**Shops in range**")
    if not nearby_shops:
        st.info("No shops found within the selected radius.")
    else:
        for shop in sorted(nearby_shops, key=lambda s: haversine(user_lat, user_lng, s["lat"], s["lng"])):
            dist = haversine(user_lat, user_lng, shop["lat"], shop["lng"])
            if shop["id"] in basket_totals:
                total = basket_totals[shop["id"]]
                is_cheapest = shop["id"] == cheapest_shop_id
                dot = "🟢" if is_cheapest else "🔴"
                price_line = f"Basket: £{total:.2f}"
            else:
                dot = "🔵"
                price_line = "No prices yet"

            st.markdown(f"{dot} **{shop['name']}**")
            st.caption(f"{distance_words(dist)} · {price_line}")

    st.divider()

    if st.session_state.basket:
        st.markdown("**Your basket**")
        for item in st.session_state.basket:
            st.write(f"• {item['name']}")
        st.caption("Go to **Home** to add more items.")
    else:
        st.info("Add items on the home page to see basket totals here.")

st.divider()
st.subheader("All prices at nearby shops")

cat_products = (
    [p for p in PRODUCTS if p["category"] == category_filter]
    if category_filter != "All categories"
    else PRODUCTS
)

if not cat_products:
    st.write("No products in that category.")
else:
    from utils import db_get_price_rows
    product_pick = st.selectbox(
        "Pick a product to compare",
        [p["name"] for p in cat_products],
        key="map_product_pick",
    )
    selected = next((p for p in cat_products if p["name"] == product_pick), None)
    if selected:
        rows = db_get_price_rows(selected["id"])
        if not rows:
            st.write("No prices reported for this item yet.")
        else:
            for i, r in enumerate(rows):
                dist = haversine(user_lat, user_lng, r["lat"], r["lng"])
                badge = " 🏆 Cheapest" if i == 0 else f"  (+£{r['price'] - rows[0]['price']:.2f})"
                st.write(
                    f"**{r['shop']}** — £{r['price']:.2f}{badge} — {distance_words(dist)}"
                )
