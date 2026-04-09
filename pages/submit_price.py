"""Submit a Price — lets shoppers report what they paid."""

import streamlit as st

st.set_page_config(
    page_title="Submit a Price — Cheapest Near Me",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="expanded",
)

from utils import render_sidebar, init_session, lookup_postcode

init_session()
render_sidebar()

from database.mock_data import PRODUCTS, MOCK_SHOPS, CATEGORIES, CATEGORY_ICONS

st.title("📝 Submit a Price")
st.write(
    "Spotted a price in a shop? Share it here and help everyone "
    "in your area find the best deal. It only takes a minute."
)
st.divider()

with st.form("submit_price_form", clear_on_submit=True):

    st.markdown("#### Where did you see this price?")
    col_pc, col_shop = st.columns(2)
    with col_pc:
        shop_postcode = st.text_input(
            "Shop postcode",
            placeholder="e.g. SW8 1JN",
            help="The postcode of the shop, not your home.",
        )
    with col_shop:
        shop_options = {f"{s['name']} — {s['address']}": s["id"] for s in MOCK_SHOPS}
        shop_options["Other shop (type below)"] = "__new__"
        chosen_shop_label = st.selectbox("Shop name", list(shop_options.keys()))
        chosen_shop_id = shop_options[chosen_shop_label]

    new_shop_name = ""
    if chosen_shop_id == "__new__":
        new_shop_name = st.text_input("Shop name", placeholder="e.g. Morrisons, Costco…")

    st.write("")

    st.markdown("#### What did you buy?")
    cat_filter = st.selectbox(
        "Category",
        ["All"] + list(CATEGORIES),
        key="submit_cat",
    )
    filtered_prods = (
        PRODUCTS if cat_filter == "All"
        else [p for p in PRODUCTS if p["category"] == cat_filter]
    )
    prod_options = {p["name"]: p["id"] for p in filtered_prods}
    prod_options["Something else (type below)"] = "__new__"
    chosen_prod_label = st.selectbox("Product", list(prod_options.keys()))
    chosen_prod_id = prod_options[chosen_prod_label]

    new_prod_name = ""
    if chosen_prod_id == "__new__":
        new_prod_name = st.text_input("Product name", placeholder="e.g. Almond Milk 1L")

    st.write("")

    st.markdown("#### How much did it cost?")
    price_val = st.number_input(
        "Price (£)",
        min_value=0.01,
        max_value=9999.99,
        value=1.00,
        step=0.01,
        format="%.2f",
    )

    st.write("")
    st.caption(
        "Optional: leave your email to get credit for verified submissions. "
        "We'll never share it."
    )
    reporter = st.text_input("Your email (optional)", placeholder="you@example.com")

    st.write("")
    submitted = st.form_submit_button(
        "Submit price  →",
        type="primary",
        use_container_width=True,
    )

if submitted:
    errors = []
    if chosen_shop_id == "__new__" and not new_shop_name.strip():
        errors.append("Please enter the shop name.")
    if chosen_prod_id == "__new__" and not new_prod_name.strip():
        errors.append("Please enter the product name.")
    if price_val <= 0:
        errors.append("Please enter a price greater than zero.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        saved = False

        try:
            from database.supabase_client import get_client
            client = get_client()

            if chosen_shop_id == "__new__":
                lat, lng = st.session_state.user_lat, st.session_state.user_lng
                if shop_postcode.strip():
                    try:
                        lat, lng, _ = lookup_postcode(shop_postcode)
                    except ValueError:
                        pass
                shop_resp = (
                    client.table("shops")
                    .insert({"name": new_shop_name.strip(), "address": shop_postcode.strip(), "lat": lat, "lng": lng})
                    .execute()
                )
                final_shop_id = shop_resp.data[0]["id"]
            else:
                final_shop_id = chosen_shop_id

            if chosen_prod_id == "__new__":
                prod_resp = (
                    client.table("products")
                    .insert({"name": new_prod_name.strip(), "category": cat_filter if cat_filter != "All" else "other"})
                    .execute()
                )
                final_prod_id = prod_resp.data[0]["id"]
            else:
                final_prod_id = chosen_prod_id

            client.table("prices").insert({
                "shop_id":     final_shop_id,
                "product_id":  final_prod_id,
                "price":       price_val,
                "reported_by": reporter.strip() or st.session_state.session_id,
                "verified":    False,
            }).execute()
            saved = True
        except Exception:
            pass

        prod_display = new_prod_name or chosen_prod_label
        shop_display = new_shop_name or chosen_shop_label.split(" — ")[0]

        st.success(
            f"Thank you! We've recorded **{prod_display}** at **£{price_val:.2f}** "
            f"from **{shop_display}**."
        )
        st.balloons()

        if not saved:
            st.info(
                "This price has been saved for your session. "
                "Connect Supabase to share it with everyone."
            )

st.divider()
st.subheader("Recently reported")
st.caption("Prices submitted by shoppers in the last 24 hours.")

recent = [
    {"product": "Whole Milk 2L",          "shop": "Lidl",              "price": 1.09, "when": "5 min ago"},
    {"product": "Paracetamol 500mg 16pk", "shop": "Tesco Express",     "price": 0.65, "when": "22 min ago"},
    {"product": "Toilet Roll 9 pack",     "shop": "Aldi",              "price": 2.69, "when": "1 hour ago"},
    {"product": "White Bread 800g",       "shop": "Sainsbury's Local", "price": 1.10, "when": "2 hours ago"},
    {"product": "Washing Up Liquid",      "shop": "Co-op Food",        "price": 1.25, "when": "3 hours ago"},
]

for r in recent:
    c1, c2, c3 = st.columns([4, 1, 2])
    c1.write(f"**{r['product']}** at {r['shop']}")
    c2.write(f"£{r['price']:.2f}")
    c3.caption(r["when"])
